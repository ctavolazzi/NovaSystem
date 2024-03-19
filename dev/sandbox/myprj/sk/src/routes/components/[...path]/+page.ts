import type { PageLoad } from "./$types"

export const load: PageLoad = async function ({
  params: { path },
}) {
  return { path }
}