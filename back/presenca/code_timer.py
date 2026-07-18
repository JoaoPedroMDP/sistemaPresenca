import logging
import threading

from django.db import close_old_connections


lgr = logging.getLogger(__name__)


class _EventCodeTimer:
    """
        Thread que rotaciona o código de um evento a cada Code.rotation_seconds()
        (configurável em runtime via Config) e envia o novo código para o grupo
        do evento via websocket.
    """
    def __init__(self, event_id: int, group_name: str):
        self.event_id = event_id
        self.group_name = group_name
        self.listeners = 0
        self.stop_signal = threading.Event()
        self.thread = threading.Thread(
            target=self._run,
            daemon=True,
            name=f"code-timer-{group_name}"
        )

    def start(self):
        self.thread.start()

    def stop(self):
        self.stop_signal.set()

    def _rotation_seconds(self) -> int:
        from presenca.models import Code

        try:
            return Code.rotation_seconds()
        except Exception:
            # Sem DB não há rotação; espera e tenta de novo no próximo tick
            lgr.exception("Erro ao ler CODE_ROTATION_SECONDS da Config, usando padrão")
            return 60

    def _run(self):
        # Imports adiados para evitar import circular com ws_controller
        from presenca.controllers.ws_controller import WsController
        from presenca.models import Event

        lgr.info(f"Timer de código iniciado para o grupo '{self.group_name}'")
        while not self.stop_signal.wait(self._rotation_seconds()):
            try:
                event = Event.objects.get(id=self.event_id)
                WsController.rotate_code_for_event(event)
            except Exception:
                lgr.exception(f"Erro ao rotacionar código do grupo '{self.group_name}'")
            finally:
                close_old_connections()

        close_old_connections()
        lgr.info(f"Timer de código encerrado para o grupo '{self.group_name}'")


class CodeTimerRegistry:
    """
        Um timer por evento. Primeiro ouvinte inicia a thread,
        último ouvinte a encerra.
    """
    _timers: dict[str, _EventCodeTimer] = {}
    _lock = threading.Lock()

    @classmethod
    def add_listener(cls, event) -> None:
        group_name = event.as_websocket_group_name()
        with cls._lock:
            timer = cls._timers.get(group_name)
            if timer is None:
                timer = _EventCodeTimer(event.id, group_name)
                cls._timers[group_name] = timer
                timer.start()
            timer.listeners += 1
            lgr.debug(f"Grupo '{group_name}' agora com {timer.listeners} ouvinte(s)")

    @classmethod
    def remove_listener(cls, group_name: str) -> None:
        with cls._lock:
            timer = cls._timers.get(group_name)
            if timer is None:
                return

            timer.listeners -= 1
            lgr.debug(f"Grupo '{group_name}' agora com {timer.listeners} ouvinte(s)")
            if timer.listeners <= 0:
                timer.stop()
                del cls._timers[group_name]
