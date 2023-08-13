import Main from "./components/main";
import { createRoot } from "react-dom/client";

// RENDERAPP
const container = document.getElementById("app");
if (container == null) {
  throw new Error();
}
const root = createRoot(container); // createRoot(container!) if you use TypeScript
root.render(<Main />);
