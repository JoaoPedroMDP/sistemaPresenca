<script lang="ts">
    import PartyHat from '$lib/assets/partyhat.png';
    import photoPlaceholder from '$lib/assets/profileAzul.png';

    interface Props {
        name: string;
        /** URL da foto; sem foto cai no placeholder, igual ao PhotoSelector */
        photo?: string | null;
        /** Semana do aniversário: ganha chapéu */
        birthday?: boolean;
        /** Lado da foto em px */
        size?: number;
        showName?: boolean;
    }

    let {
        name,
        photo = null,
        birthday = false,
        size = 80,
        showName = true
    }: Props = $props();
</script>

<div class="member" style="--member-photo-size: {size}px">
    <div class="member-photo-wrap">
        {#if birthday}
            <img src={PartyHat} class="member-hat" alt="Chapéu de aniversário" />
        {/if}
        <img
            class="member-photo"
            src={photo || photoPlaceholder}
            alt={name}
            width={size}
            height={size}
            decoding="async"
        />
    </div>
    {#if showName}
        <span class="member-name">{name}</span>
    {/if}
</div>

<style>
    .member {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 6px;
        /* Dentro de grid/flex apertado o item precisa poder encolher o nome
           sem espremer a foto */
        min-width: 0;
        max-width: 100%;
    }

    .member-photo-wrap {
        position: relative;
        line-height: 0;
        flex: 0 0 auto;
    }

    .member-photo {
        display: block;
        width: var(--member-photo-size);
        height: var(--member-photo-size);
        border-radius: 9999px;
        object-fit: cover;
        border: 2px solid var(--color-indigo-900);
        background: white;
    }

    .member-name {
        font-size: 15px;
        font-weight: 600;
        color: var(--color-indigo-950);
        text-align: center;
        line-height: 1.25;
        /* Nunca passa da largura do card; nome comprido quebra em até duas
           linhas e só então recebe reticências */
        max-width: 100%;
        display: -webkit-box;
        -webkit-box-orient: vertical;
        -webkit-line-clamp: 2;
        line-clamp: 2;
        overflow: hidden;
        overflow-wrap: anywhere;
    }

    .member-hat {
        position: absolute;
        right: -1rem;
        top: -1rem;
        width: 2.5rem;
        height: 2.5rem;
        transform: rotate(30deg);
        object-fit: contain;
        pointer-events: none;
        z-index: 1;
    }

</style>
