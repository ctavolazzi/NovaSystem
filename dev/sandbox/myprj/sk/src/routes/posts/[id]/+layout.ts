import { client } from "$lib/pocketbase";
import type { PostsResponse } from "$lib/pocketbase/pocketbase-types";
import type { LayoutLoad } from "./$types";

export const load: LayoutLoad = async ({ params: { id } }) => {
  const record =
    id === "new"
      ? ({} as PostsResponse)
      : await client.collection("posts").getOne<PostsResponse>(id);
  return {
    record,
  };
};
