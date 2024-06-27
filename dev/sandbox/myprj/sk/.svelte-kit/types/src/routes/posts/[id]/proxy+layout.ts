// @ts-nocheck
import { client } from "$lib/pocketbase";
import type { PostsResponse } from "$lib/pocketbase/pocketbase-types";
import type { LayoutLoad } from "./$types";

export const load = async ({ params: { id } }: Parameters<LayoutLoad>[0]) => {
  const record =
    id === "new"
      ? ({} as PostsResponse)
      : await client.collection("posts").getOne<PostsResponse>(id);
  return {
    record,
  };
};
