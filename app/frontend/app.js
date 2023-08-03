import React from "react";
import ReactDOM from "react-dom";
import Main from "./components/main";
import { createRoot } from "react-dom/client";

// RENDERAPP
const container = document.getElementById("app");
const root = createRoot(container); // createRoot(container!) if you use TypeScript
root.render(<Main />);
