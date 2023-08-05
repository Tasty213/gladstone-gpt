import React, { useState } from "react";

function CanvassForm({ setCompleted, setUserId }) {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [postCode, setPostCode] = useState("");
  const [email, setEmail] = useState("");
  const [voterIntent, setVoterIntent] = useState("Liberal Democrat");

  return (
    <form
      class="user-input-form"
      onSubmit={(e) =>
        submitForm(
          e,
          setCompleted,
          setUserId,
          firstName,
          lastName,
          postCode,
          email,
          voterIntent
        )
      }
    >
      <input
        type="text"
        id="first-name"
        class="user-input-box"
        value={firstName}
        placeholder="First name"
        onChange={(e) => setFirstName(e.target.value)}
      ></input>
      <input
        type="text"
        id="last-name"
        class="user-input-box"
        value={lastName}
        placeholder="Last name"
        onChange={(e) => setLastName(e.target.value)}
      ></input>
      <input
        type="text"
        id="post-code"
        class="user-input-box"
        value={postCode}
        placeholder="Post Code"
        onChange={(e) => setPostCode(e.target.value)}
      ></input>
      <input
        type="email"
        id="email"
        class="user-input-box"
        value={email}
        placeholder="Email"
        onChange={(e) => setEmail(e.target.value)}
      ></input>
      <select
        id="voter-intent"
        value={voterIntent}
        placeholder="Voter Intent"
        onChange={(e) => setVoterIntent(e.target.value)}
        class="user-input-box"
      >
        <option>Liberal Democrat</option>
        <option>Conservative</option>
        <option>Labour</option>
        <option>Green</option>
        <option>Independent</option>
      </select>
      <button id="send-button" class="enabled">
        Submit
      </button>
    </form>
  );
}

function submitForm(
  event,
  setCompleted,
  setUserId,
  firstName,
  lastName,
  postcode,
  email,
  voterIntent
) {
  event.preventDefault();
  userId = crypto.randomUUID();
  setUserId(userId);

  canvassData = {
    userId: userId,
    firstName: firstName,
    lastName: lastName,
    postcode: postcode,
    email: email,
    voterIntent: voterIntent,
    time: Date.now(),
  };

  fetch("/submit_canvass", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(canvassData),
  });

  setCompleted(true);
}

export default CanvassForm;