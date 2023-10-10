import { useEffect, useState } from "react";
import Chat from "./chat";

const Main = () => {
  const [userId, setUserId] = useState(crypto.randomUUID());
  const [localPartyDetails, setLocalPartyDetails] = useState("");

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
      <Chat userId={userId} localPartyDetails={localPartyDetails} />
    </div>
  );
};

export default Main;
