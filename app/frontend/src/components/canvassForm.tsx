import React, { useState } from "react";

type CanvassFormProps = {
  setCompleted: React.Dispatch<React.SetStateAction<boolean>>;
  setUserId: React.Dispatch<React.SetStateAction<string>>;
  setLocalPartyDetails: React.Dispatch<React.SetStateAction<string>>;
};

function CanvassForm({
  setCompleted,
  setUserId,
  setLocalPartyDetails,
}: CanvassFormProps) {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [postCode, setPostCode] = useState("");
  const [email, setEmail] = useState("");
  const [voterIntent, setVoterIntent] = useState("Liberal Democrat");

  return (
    <form
      className="user-input-form"
      onSubmit={(e) =>
        doCaptchaThenSubmitForm(
          e,
          setCompleted,
          setUserId,
          setLocalPartyDetails,
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
        className="user-input-box"
        value={firstName}
        placeholder="First name"
        onChange={(e) => setFirstName(e.target.value)}
      ></input>
      <input
        type="text"
        id="last-name"
        className="user-input-box"
        value={lastName}
        placeholder="Last name"
        onChange={(e) => setLastName(e.target.value)}
      ></input>
      <input
        type="text"
        id="post-code"
        className="user-input-box"
        value={postCode}
        placeholder="Post Code"
        onChange={(e) => setPostCode(e.target.value)}
      ></input>
      <input
        type="email"
        id="email"
        className="user-input-box"
        value={email}
        placeholder="Email"
        onChange={(e) => setEmail(e.target.value)}
      ></input>
      <select
        id="voter-intent"
        value={voterIntent}
        placeholder="Voter Intent"
        onChange={(e) => setVoterIntent(e.target.value)}
        className="user-input-box"
      >
        <option>Liberal Democrat</option>
        <option>Conservative</option>
        <option>Labour</option>
        <option>Green</option>
        <option>Independent</option>
      </select>
      <button id="send-button" className="enabled">
        Submit
      </button>
    </form>
  );
}

function doCaptchaThenSubmitForm(
  event: React.FormEvent<HTMLFormElement>,
  setCompleted: React.Dispatch<React.SetStateAction<boolean>>,
  setUserId: React.Dispatch<React.SetStateAction<string>>,
  setLocalPartyDetails: React.Dispatch<React.SetStateAction<string>>,
  firstName: string,
  lastName: string,
  postcode: string,
  email: string,
  voterIntent: string
) {
  event.preventDefault();
  window.grecaptcha.ready(() => {
    window.grecaptcha
      .execute("6LftMhQoAAAAAPhghGEe6eUxV4QhUnaG4Vyxg5mf", { action: "submit" })
      .then((token: string) => {
        submitForm(
          setCompleted,
          setUserId,
          setLocalPartyDetails,
          token,
          firstName,
          lastName,
          postcode,
          email,
          voterIntent
        );
      });
  });
}

function submitForm(
  setCompleted: React.Dispatch<React.SetStateAction<boolean>>,
  setUserId: React.Dispatch<React.SetStateAction<string>>,
  setLocalPartyDetails: React.Dispatch<React.SetStateAction<string>>,
  token: string,
  firstName: string,
  lastName: string,
  postcode: string,
  email: string,
  voterIntent: string
) {
  const userId = crypto.randomUUID();
  setUserId(userId);

  const canvassData = {
    captcha: token,
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
  })
    .then((response) => {
      if (!response.ok) throw new Error(response.statusText);
      else return response.json();
    })
    .then((data) => {
      setLocalPartyDetails(data.local_party_details);
    });

  setCompleted(true);
}

export default CanvassForm;
