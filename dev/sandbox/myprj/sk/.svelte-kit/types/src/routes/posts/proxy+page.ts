// @ts-nocheck
import { watch } from "$lib/pocketbase";
import type { PostsRecord, PostsResponse } from "$lib/pocketbase/pocketbase-types";
import type { PageLoad } from "./$types";

export const load = async () => {
  const posts = await watch<PostsResponse>("posts");
  return {
    posts,
  };
};
;null as any as PageLoad;