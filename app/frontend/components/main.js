import React, { useState } from "react";
import Chat from "./chat";
import CanvassForm from "./canvassForm";

const Main = () => {
  const [canvassComplete, setCanvassComplete] = useState(false);
  const [userId, setUserId] = useState("");

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
