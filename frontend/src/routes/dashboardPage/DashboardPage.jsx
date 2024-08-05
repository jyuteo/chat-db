import "./dashboardPage.css";
import { useNavigate } from "react-router-dom";
import { useState } from "react";

const DashboardPage = () => {
  const navigate = useNavigate();

  const [showForm, setShowForm] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isUsingExampleDB, setIsUsingExampleDB] = useState(false);
  const [error, setError] = useState("");

  const addNewChatSessionId = (newChatSessionId, dbHost, dbPort, dbName) => {
    let chatSessionIds =
      JSON.parse(localStorage.getItem("chat_session_ids")) || [];
    chatSessionIds.push(newChatSessionId);
    localStorage.setItem("chat_session_ids", JSON.stringify(chatSessionIds));
    localStorage.setItem(
      `chat_session_info_${newChatSessionId}`,
      JSON.stringify({ dbHost, dbPort, dbName })
    );
    window.dispatchEvent(new Event("storage"));
  };

  const toggleForm = () => {
    setShowForm(!showForm);
  };

  const exampleDBConnConfig = {
    dbType: `${import.meta.env.VITE_EXAMPLE_DB_TYPE}`,
    dbHost: `${import.meta.env.VITE_EXAMPLE_DB_HOST}`,
    dbPort: `${import.meta.env.VITE_EXAMPLE_DB_PORT}`,
    dbName: `${import.meta.env.VITE_EXAMPLE_DB_NAME}`,
    user: `${import.meta.env.VITE_EXAMPLE_DB_USER}`,
    password: `${import.meta.env.VITE_EXAMPLE_DB_PASSWORD}`,
  };

  const [formValues, setFormValues] = useState({
    dbType: "",
    dbHost: "",
    dbPort: "",
    dbName: "",
    user: "",
    password: "",
    llmClient: "",
    llmApiKey: "",
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormValues({
      ...formValues,
      [name]: value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const {
      dbType,
      dbHost,
      dbPort,
      dbName,
      user,
      password,
      llmClient,
      llmApiKey,
    } = formValues;

    if (
      !dbType ||
      !dbHost ||
      !dbPort ||
      !dbName ||
      !user ||
      !password ||
      !llmClient ||
      !llmApiKey
    ) {
      alert("Please fill in all the fields");
      return;
    }

    setIsLoading(true);
    setError("");

    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/chat/create`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            llm: {
              type: formValues.llmClient,
              config: {
                api_key: formValues.llmApiKey,
              },
            },
            db: {
              type: formValues.dbType,
              config: {
                host: formValues.dbHost,
                user: formValues.user,
                password: isUsingExampleDB ? undefined : formValues.password,
                database: formValues.dbName,
                port: formValues.dbPort,
              },
            },
          }),
          credentials: "include",
        }
      );

      if (!response.ok) {
        const data = await response.json();
        setError(data.msg || "An error occurred while creating the chat");
        console.log(data.trace);
        return;
      }
      const data = await response.json();
      addNewChatSessionId(data.chat_session_id, dbHost, dbPort, dbName);
      navigate(`/chat/${data.chat_session_id}`);
    } catch (err) {
      console.log(err);
      setError(err || "An error occurred while creating the chat");
    } finally {
      setIsLoading(false);
    }
  };

  const handleExampleDBClick = () => {
    setIsUsingExampleDB(true);
    setFormValues({
      ...exampleDBConnConfig,
      llmClient: formValues.llmClient,
      llmApiKey: formValues.llmApiKey,
    });
    setShowForm(true);
  };

  return (
    <div className="dashboardPage">
      <div className="texts">
        <div className="logo">
          <img src="/logo.png" alt="Logo" />
          <h1>ChatDB</h1>
        </div>
        <div className="dbFormContainer">
          {!isLoading ? (
            !showForm ? (
              <div className="messageContainer">
                <div className="message" onClick={toggleForm}>
                  <img src="/chat.png" alt="" />
                  <span>Connect to your DB and start chatting</span>
                </div>
                <div className="message" onClick={handleExampleDBClick}>
                  <img src="/chat.png" alt="" />
                  <span>Connect to a public DB and start chatting</span>
                  <span>(you only need to provide your LLM api key)</span>
                </div>
              </div>
            ) : (
              <form onSubmit={handleSubmit}>
                <select
                  name="dbType"
                  value={formValues.dbType}
                  onChange={handleInputChange}
                >
                  <option value="">Select Database Type</option>
                  <option value="mysql">MySQL</option>
                </select>
                <input
                  type="text"
                  placeholder="Database Host"
                  name="dbHost"
                  value={formValues.dbHost}
                  onChange={handleInputChange}
                />
                <input
                  type="text"
                  placeholder="Database Port"
                  name="dbPort"
                  value={formValues.dbPort}
                  onChange={handleInputChange}
                />
                <input
                  type="text"
                  placeholder="Database User"
                  name="user"
                  value={formValues.user}
                  onChange={handleInputChange}
                />
                <input
                  type="password"
                  placeholder="Password"
                  name="password"
                  value={formValues.password}
                  onChange={handleInputChange}
                />
                <input
                  type="text"
                  placeholder="Database Name"
                  name="dbName"
                  value={formValues.dbName}
                  onChange={handleInputChange}
                />
                <select
                  name="llmClient"
                  value={formValues.llmClient}
                  onChange={handleInputChange}
                >
                  <option value="">Select LLM Client</option>
                  <option value="gemini">Gemini</option>
                </select>
                <input
                  type="password"
                  name="llmApiKey"
                  placeholder="LLM API Key"
                  value={formValues.llmApiKey}
                  onChange={handleInputChange}
                />
                <button type="submit">
                  <span>Start conversation</span>
                </button>
                {error && <div className="error">{error}</div>}
              </form>
            )
          ) : (
            <div className="loading">
              Creating chat session....Indexing table schemas in database might
              take some time...
            </div>
          )}
        </div>
      </div>
      <div className="formContainer">
        <form>
          <input
            type="text"
            name="text"
            placeholder="Ask me anything..."
            disabled={true}
          />
          <button>
            <img src="/arrow.png" alt="Arrow" />
          </button>
        </form>
      </div>
    </div>
  );
};

export default DashboardPage;
