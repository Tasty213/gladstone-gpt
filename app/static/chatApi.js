const chatLog = document.getElementById("chat-log");
const userInputBox = document.getElementById("user-input-box");
const sendButton = document.getElementById("send-button");

function appendQuestion(message) {
    const messageDiv = document.createElement("div");
    messageDiv.className = "message user";
    messageDiv.innerText = message;
    chatLog.appendChild(messageDiv);
}

function appendAnswer(answer, sources) {
  const messageDiv = document.createElement("div");
  messageDiv.className = "message chatbot";

  let answerElement = document.createElement("p")
  answerElement.innerText = answer
  messageDiv.appendChild(answerElement)

  let uniqueSources = [...new Set(sources)]
  uniqueSources.forEach(source => {
    var sourceElement = document.createElement('a')
    sourceElement.href = source.link
    sourceElement.innerText = `${source.name}\n`
    messageDiv.appendChild(sourceElement)
  });

  chatLog.appendChild(messageDiv);
}

function sendMessage(message) {
  const userMessage = userInputBox.value;
  appendQuestion(userMessage);

  // Send the user message to the server
  fetch("/get_response", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question: userMessage }),
  })
    .then((response) => response.json())
    .then((data) => {
        appendAnswer(data.answer, data.sources);
    })
    .catch((error) => console.error("Error:", error));

  // Clear the input box after sending
  userInputBox.value = "";
}

sendButton.addEventListener("click", sendMessage);
userInputBox.addEventListener("keypress", function (event) {
  if (event.keyCode === 13) {
    sendMessage();
  }
});
