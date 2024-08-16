import { useState, useEffect } from "react";
import { useAuth } from "@clerk/clerk-react";
import { useNavigate } from "react-router-dom";
import "./knowledgeBasePage.css";

const KnowledgeBasePage = () => {
  const navigate = useNavigate();
  const { isSignedIn, userId } = useAuth();

  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [openGroups, setOpenGroups] = useState({});
  const [showAddTableForm, setShowAddTableForm] = useState(false);
  const [showAddQuestionForm, setShowAddQuestionForm] = useState(false);
  const [tableSchemaFormData, setTableFormData] = useState({
    embeddingModelType: "sentence_transformer",
    vectorStoreType: "tidb",
    dbType: "mysql",
    databaseName: "",
    tableName: "",
    tableSchema: "",
    owner: null,
  });
  const [questionSQLFormData, setQuestionFormData] = useState({
    embeddingModelType: "sentence_transformer",
    vectorStoreType: "tidb",
    dbType: "mysql",
    databaseName: "",
    tableName: "",
    question: "",
    sql: "",
    owner: null,
  });
  const [notification, setNotification] = useState("");
  const [showNotification, setShowNotification] = useState(false);

  const fetchData = async (userId) => {
    try {
      setLoading(true);
      const response = userId
        ? await fetch(
            `${
              import.meta.env.VITE_API_URL
            }/knowledge_base/get?user_id=${userId}`
          )
        : await fetch(`${import.meta.env.VITE_API_URL}/knowledge_base/get`);
      if (!response.ok) {
        throw new Error("Failed to fetch knowledge base");
      }
      const result = await response.json();
      setData(result.result || []);
    } catch (error) {
      setError(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isSignedIn && userId !== undefined) {
      fetchData(userId);
    } else if (!isSignedIn) {
      fetchData(null);
    }
  }, [isSignedIn, userId]);

  const toggleGroup = (index) => {
    setOpenGroups((prevState) => ({
      ...prevState,
      [index]: !prevState[index],
    }));
  };

  const handleSignInClick = () => {
    navigate("/sign-in");
  };

  const handleAddTableClick = () => {
    setShowAddTableForm(true);
    setShowAddQuestionForm(false);
  };

  const handleAddQuestionClick = () => {
    setShowAddTableForm(false);
    setShowAddQuestionForm(true);
  };

  const handleCloseForm = () => {
    setShowAddTableForm(false);
    setShowAddQuestionForm(false);
  };

  const handleTableFormChange = (e) => {
    const { name, value } = e.target;
    setTableFormData((prevData) => ({ ...prevData, [name]: value }));
  };

  const handleQuestionFormChange = (e) => {
    const { name, value } = e.target;
    setQuestionFormData((prevData) => ({ ...prevData, [name]: value }));
  };

  const handleFormSubmit = async (event, formType) => {
    event.preventDefault();

    if (formType === "table") {
      if (
        !tableSchemaFormData.databaseName ||
        !tableSchemaFormData.tableName ||
        !tableSchemaFormData.tableSchema ||
        !tableSchemaFormData.dbType ||
        !tableSchemaFormData.embeddingModelType ||
        !tableSchemaFormData.vectorStoreType
      ) {
        alert("Please fill in all fields.");
        return;
      }

      const requestData = {
        db_type: tableSchemaFormData.dbType,
        embedding_model_type: tableSchemaFormData.embeddingModelType,
        vector_store_type: tableSchemaFormData.vectorStoreType,
        data: [
          {
            database_name: tableSchemaFormData.databaseName,
            table_name: tableSchemaFormData.tableName,
            table_schema: tableSchemaFormData.tableSchema,
            owner: userId ? userId : null,
          },
        ],
      };

      console.log(requestData);

      try {
        const response = await fetch(
          `${import.meta.env.VITE_API_URL}/knowledge_base/add_db_table_schemas`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify(requestData),
          }
        );
        if (!response.ok) {
          throw new Error("Failed to add DB table schema.");
        }
        const result = await response.json();
        setNotification(result.message);
        setShowNotification(true);
        setTimeout(() => {
          setShowNotification(false);
        }, 3000);
        handleCloseForm();
      } catch (error) {
        setError(error.message);
      }
    } else {
      if (
        (questionSQLFormData.databaseName && !questionSQLFormData.tableName) ||
        (questionSQLFormData.tableName && !questionSQLFormData.databaseName)
      ) {
        alert("Database and table name must be provided together.");
        return;
      }
      if (
        !questionSQLFormData.question ||
        !questionSQLFormData.sql ||
        !tableSchemaFormData.dbType ||
        !tableSchemaFormData.embeddingModelType ||
        !tableSchemaFormData.vectorStoreType
      ) {
        alert("Please provide all required fields.");
        return;
      }
      const requestData = {
        db_type: questionSQLFormData.dbType,
        embedding_model_type: questionSQLFormData.embeddingModelType,
        vector_store_type: questionSQLFormData.vectorStoreType,
        data: [
          {
            database_name: questionSQLFormData.databaseName
              ? questionSQLFormData.databaseName
              : null,
            table_name: questionSQLFormData.tableName
              ? questionSQLFormData.tableName
              : null,
            question: questionSQLFormData.question,
            sql: questionSQLFormData.sql,
            owner: userId ? userId : null,
          },
        ],
      };

      console.log(requestData);

      try {
        const response = await fetch(
          `${
            import.meta.env.VITE_API_URL
          }/knowledge_base/add_question_sql_pairs`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify(requestData),
          }
        );
        if (!response.ok) {
          throw new Error("Failed to add question SQL.");
        }
        const result = await response.json();
        setNotification(result.message);
        setShowNotification(true);
        setTimeout(() => {
          setShowNotification(false);
        }, 3000);
        handleCloseForm();
      } catch (error) {
        setError(error.message);
      }
    }
  };

  if (loading) return <div className="loading">Loading...</div>;
  if (error) return <div className="error">Error: {error.message}</div>;

  return (
    <div className="knowledge-base-page">
      <div className="top-bar">
        {userId ? (
          <>
            <button onClick={handleAddTableClick}>Add Table Schema</button>
            <button onClick={handleAddQuestionClick}>Add SQL Question</button>
          </>
        ) : (
          <button onClick={handleSignInClick}>
            Sign in to create your knowledge base
          </button>
        )}
      </div>

      {showAddTableForm && (
        <div className="form-container">
          <div className="form">
            <h2>Add Table Schema</h2>
            <form onSubmit={(e) => handleFormSubmit(e, "table")}>
              <label>
                Databse type:
                <select
                  name="dbType"
                  value={tableSchemaFormData.dbType}
                  onChange={handleQuestionFormChange}
                >
                  <option value="">Select Database Type</option>
                  <option value="mysql">MySQL</option>
                </select>
              </label>
              <label>
                Embedding model type:
                <select
                  name="embeddingModelType"
                  value={tableSchemaFormData.embeddingModelType}
                  onChange={handleQuestionFormChange}
                >
                  <option value="">Select Embedding Model Type</option>
                  <option value="sentence_transformer">
                    Sentence transformer
                  </option>
                </select>
              </label>
              <label>
                Database Name:
                <input
                  type="text"
                  name="databaseName"
                  value={tableSchemaFormData.databaseName}
                  onChange={handleTableFormChange}
                  required
                />
              </label>
              <label>
                Table Name:
                <input
                  type="text"
                  name="tableName"
                  value={tableSchemaFormData.tableName}
                  onChange={handleTableFormChange}
                  required
                />
              </label>
              <label>
                Table Schema:
                <textarea
                  name="tableSchema"
                  value={tableSchemaFormData.tableSchema}
                  onChange={handleTableFormChange}
                  required
                ></textarea>
              </label>
              <div className="button-container">
                <button type="submit" className="submit-button">
                  Submit
                </button>
                <button
                  type="button"
                  className="close-button"
                  onClick={handleCloseForm}
                >
                  Close
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showAddQuestionForm && (
        <div className="form-container">
          <div className="form">
            <h2>Add SQL Question</h2>
            <form onSubmit={(e) => handleFormSubmit(e, "question")}>
              <label>
                Database type:
                <select
                  name="dbType"
                  value={questionSQLFormData.dbType}
                  onChange={handleQuestionFormChange}
                >
                  <option value="">Select Database Type</option>
                  <option value="mysql">MySQL</option>
                </select>
              </label>
              <label>
                Embedding model type:
                <select
                  name="embeddingModelType"
                  value={questionSQLFormData.embeddingModelType}
                  onChange={handleQuestionFormChange}
                >
                  <option value="">Select Embedding Model Type</option>
                  <option value="sentence_transformer">
                    Sentence transformer
                  </option>
                </select>
              </label>
              <label>
                Database Name:
                <input
                  type="text"
                  name="databaseName"
                  value={questionSQLFormData.databaseName}
                  onChange={handleQuestionFormChange}
                />
              </label>
              <label>
                Table Name:
                <input
                  type="text"
                  name="tableName"
                  value={questionSQLFormData.tableName}
                  onChange={handleQuestionFormChange}
                />
              </label>
              <label>
                Question:
                <textarea
                  name="question"
                  value={questionSQLFormData.question}
                  onChange={handleQuestionFormChange}
                  required
                ></textarea>
              </label>
              <label>
                SQL Query:
                <textarea
                  name="sql"
                  value={questionSQLFormData.sql}
                  onChange={handleQuestionFormChange}
                  required
                ></textarea>
              </label>
              <div className="button-container">
                <button type="submit" className="submit-button">
                  Submit
                </button>
                <button
                  type="button"
                  className="close-button"
                  onClick={handleCloseForm}
                >
                  Close
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showNotification && <div className="notification">{notification}</div>}

      {data.map((item, index) => (
        <div key={index} className="table-info">
          <div className="group-header" onClick={() => toggleGroup(index)}>
            <span className="toggle-arrow">
              {openGroups[index] ? "▲" : "▼"}
            </span>
            <h2 className="table-name">
              {item.db_table_info.database_name || "unknown_database"}.
              {item.db_table_info.table_name || "unknown_table"}
            </h2>
            <p className="owner-name">
              Owner: {item.db_table_info.owner || "unknown"}
            </p>
          </div>
          {openGroups[index] && (
            <>
              <div className="table-details">
                <pre className="table-schema">
                  {item.db_table_info.table_schema || "No schema available"}
                </pre>
              </div>
              <div className="sql-questions">
                <h3>SQL Questions</h3>
                {item.sql_question_pair.length ? (
                  item.sql_question_pair.map((pair, idx) => (
                    <div key={idx} className="sql-question">
                      <p className="question">
                        <strong>Question:</strong> {pair.question}
                      </p>
                      <pre className="sql-code">{pair.sql}</pre>
                    </div>
                  ))
                ) : (
                  <p>No questions available</p>
                )}
              </div>
            </>
          )}
        </div>
      ))}
    </div>
  );
};

export default KnowledgeBasePage;
