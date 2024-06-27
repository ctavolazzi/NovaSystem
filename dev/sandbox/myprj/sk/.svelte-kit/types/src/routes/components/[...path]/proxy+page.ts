// @ts-nocheck
import type { PageLoad } from "./$types"

export const load = async function ({
  params: { path },
}: Parameters<PageLoad>[0]) {
  return { path }
}