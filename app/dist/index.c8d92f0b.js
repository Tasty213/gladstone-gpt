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
    let answerElement = document.createElement("p");
    answerElement.innerText = answer;
    messageDiv.appendChild(answerElement);
    let uniqueSources = {};
    sources.forEach((element)=>uniqueSources[`${element.link}-page-${element.page_number}`] = element);
    Object.entries(uniqueSources).forEach((source)=>{
        var sourceElement = document.createElement("a");
        sourceElement.href = source[1].link;
        if (source[1].page_number) sourceElement.innerText = `${source[1].name} - page ${source[1].page_number}\n`;
        else sourceElement.innerText = `${source[1].name}\n`;
        messageDiv.appendChild(sourceElement);
    });
    chatLog.appendChild(messageDiv);
    sendButton.disabled = false;
    sendButton.className = "enabled";
}
function sendMessage(message) {
    const userMessage = userInputBox.value;
    sendButton.disabled = true;
    sendButton.className = "disabled";
    appendQuestion(userMessage);
    // Send the user message to the server
    fetch("/get_response", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            question: userMessage
        })
    }).then((response)=>response.json()).then((data)=>{
        appendAnswer(data.answer, data.sources);
    }).catch((error)=>console.error("Error:", error));
    // Clear the input box after sending
    userInputBox.value = "";
}
sendButton.addEventListener("click", sendMessage);
userInputBox.addEventListener("keypress", function(event) {
    if (event.keyCode === 13) sendMessage();
});

//# sourceMappingURL=index.c8d92f0b.js.map
