import { writable } from "svelte/store";

export const remotePath = writable(
  localStorage.getItem("remotePath") || "vscode://vscode-remote/ssh-remote+office"
);

remotePath.subscribe(($remotePath) => {
  localStorage.setItem("remotePath", $remotePath);
});

export function cleanComponentPath(path: string) {
  let newPath = path.replace(".svelte/", ".svelte");
  return newPath;
}

// There is no real typescript type for input types
export type HTMLInputTypes =
  | "button"
  | "checkbox"
  | "color"
  | "date"
  | "datetime-local"
  | "email"
  | "file"
  | "hidden"
  | "image"
  | "month"
  | "number"
  | "password"
  | "radio"
  | "range"
  | "reset"
  | "search"
  | "submit"
  | "tel"
  | "text"
  | "time"
  | "url"
  | "week"
  | (string & {});

interface CustomInput {
  type: HTMLInputTypes;
  attributes?: any;
  processor?: Function;
}

export const INPUT_TYPES: { [key: string]: CustomInput } = {
  text: {
    type: "text",
    processor: (x: string) => x,
  },
  date: {
    type: "date",
    processor: (x: string) => {
      return new Date(x);
    },
  },
  number: {
    type: "number",
  },
};
