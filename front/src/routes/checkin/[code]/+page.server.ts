import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({fetch, params}) => {
    const response = await fetch(`/api/ponto/members/pending/${params.code}`);
    let parsed = await response.json();

    if(parsed.error){
        error(parsed.error_code, parsed.error);
    }

    return parsed;
};