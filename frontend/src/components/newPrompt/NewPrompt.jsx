import { useEffect, useRef, useState, useCallback } from "react";
import "./newPrompt.css";
import Markdown from "react-markdown";
import Message from "../message/Message";

const NewPrompt = ({ chatSessionId, updateChat }) => {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [isAnswered, setIsAnswered] = useState(false);
  const [inputText, setInputText] = useState("");

  const endRef = useRef(null);
  const formRef = useRef(null);

  useEffect(() => {
    setQuestion("");
    setAnswer({});
    setIsLoading(false);
    setError("");
    setIsAnswered(false);
  }, [chatSessionId]);

  useEffect(() => {
    endRef.current.scrollIntoView({ behavior: "smooth" });
  }, [question, answer]);

  useEffect(() => {
    if (isAnswered) {
      const chatHistory = JSON.parse(localStorage.getItem(chatSessionId)) || [];

      chatHistory.push({
        role: "user",
        msg: question,
        sql: undefined,
        data: undefined,
        naturalLanguageAnswer: undefined,
      });

      if (!error) {
        chatHistory.push({
          role: "bot",
          msg: answer.message,
          sql: answer.sql,
          data: answer.data,
          naturalLanguageAnswer: answer.natural_language_answer,
        });
      } else {
        chatHistory.push({
          role: "bot",
          msg: error,
          sql: undefined,
          data: undefined,
          naturalLanguageAnswer: undefined,
        });
      }

      localStorage.setItem(chatSessionId, JSON.stringify(chatHistory));
      setIsAnswered(false);
      updateChat();
    }
  }, [isAnswered, chatSessionId, updateChat, question, answer, error]);

  const add = useCallback(
    async (question) => {
      setQuestion(question);
      setAnswer({});
      setIsLoading(true);
      setError("");

      try {
        const response = await fetch(
          `${import.meta.env.VITE_API_URL}/chat/send_message`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ question, chat_session_id: chatSessionId }),
            credentials: "include",
          }
        );

        if (!response.ok) {
          const data = await response.json();
          setError(
            data.msg ||
              "An error occurred while generating answer for the question"
          );
          console.log(data.trace);
          return;
        }

        const data = await response.json();
        setAnswer(data.result);
        setIsAnswered(true);
      } catch (err) {
        console.log(err);
        setError("An error occurred while generating answer for the question");
        setIsAnswered(true);
      } finally {
        setIsLoading(false);
      }
    },
    [chatSessionId]
  );

  const handleSubmit = useCallback(
    async (e) => {
      e.preventDefault();

      const text = e.target.text.value;
      if (!text) return;
      e.target.text.value = "";
      setInputText("");
      add(text);
    },
    [add]
  );

  const handleInputChange = (e) => {
    setInputText(e.target.value);
  };

  const message = answer
    ? {
        role: "bot",
        msg: answer.message,
        sql: answer.sql,
        data: answer.data,
        naturalLanguageAnswer: answer.natural_language_answer,
      }
    : error
    ? {
        role: "bot",
        msg: error,
        sql: undefined,
        data: undefined,
        naturalLanguageAnswer: undefined,
      }
    : null;

  return (
    <>
      {question && <div className="message user">{question}</div>}
      {isLoading && (
        <div className="message">
          <Markdown>Generating answer...</Markdown>
        </div>
      )}
      {message && (
        <div className="message">
          <Message message={message} />
        </div>
      )}
      {error && (
        <div className="message">
          <Markdown>{error}</Markdown>
        </div>
      )}
      <div className="endChat" ref={endRef}></div>
      <form
        className="newForm"
        ref={formRef}
        onChange={handleInputChange}
        onSubmit={handleSubmit}
        value={inputText}
      >
        <input type="text" name="text" placeholder="Ask anything..." />
        <button className={inputText ? "active" : ""}>
          <img src="/arrow.png" alt="" />
        </button>
      </form>
    </>
  );
};

export default NewPrompt;
