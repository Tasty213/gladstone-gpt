import { useEffect, useState } from "react";
import Chat from "./chat";
import CanvassForm from "./canvassForm";

const Main = () => {
  const [canvassComplete, setCanvassComplete] = useState(false);
  const [userId, setUserId] = useState("");

  const handleLoaded = (_: any) => {
    window.grecaptcha.ready((_: any) => {
      window.grecaptcha.execute("6LftMhQoAAAAAPhghGEe6eUxV4QhUnaG4Vyxg5mf", {
        action: "homepage",
      });
    });
  };

  useEffect(() => {
    // Add reCaptcha
    const script = document.createElement("script");
    script.src =
      "https://www.google.com/recaptcha/api.js?render=6LftMhQoAAAAAPhghGEe6eUxV4QhUnaG4Vyxg5mf";
    script.addEventListener("load", handleLoaded);
    document.body.appendChild(script);
  }, []);

  return (
    <div id="chat-container">
      {canvassComplete ? (
        <Chat userId={userId} />
      ) : (
        <CanvassForm setCompleted={setCanvassComplete} setUserId={setUserId} />
      )}
    </div>
  );
};

export default Main;
