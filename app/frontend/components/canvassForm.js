import React, { useState } from "react";

function CanvassForm({ setCompleted, setUserId }) {
  [firstName, setFirstName] = useState("");
  [lastName, setLastName] = useState("");
  [postCode, setPostCode] = useState("");
  [email, setEmail] = useState("");
  [voterIntent, setVoterIntent] = useState("");

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
          email
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
      >
        <option>Liberal Democrat</option>
        <option>Conservative</option>
        <option>Labour</option>
        <option>Green</option>
        <option>Independent</option>
      </select>
      <button id="submit-button">Submit</button>
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
  email
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
