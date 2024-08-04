import Markdown from "react-markdown";
import "./message.css";

const Message = ({ message }) => {
  console.log("message", message);
  const { msg = "", sql = "", data = {}, naturalLanguageAnswer = "" } = message;

  const renderTable = (data) => {
    if (typeof data !== "object" || data === null) {
      console.error("Data is not a valid object:", data);
      return null;
    }

    // Extract the first entry from data
    const entries = Object.entries(data);
    console.log("Entries:", entries);

    if (entries.length === 0) {
      return null;
    }

    const [query, rows] = entries[0];

    if (!Array.isArray(rows)) {
      console.error("Rows is not an array or is undefined:", rows);
      return <p>No valid rows found.</p>;
    }

    return (
      <div className="table-container">
        {/* <p>
          <strong>Query:</strong> {query}
        </p> */}
        <table>
          <thead>
            <tr>
              {Object.keys(rows[0]).map((key) => (
                <th key={key}>{key}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, index) => (
              <tr key={index}>
                {Object.values(row).map((value, i) => (
                  <td key={i}>{value}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <div className="message-display">
      {sql && (
        <div className="sql-content">
          <h4>SQL Query:</h4>
          <pre>
            <code>{sql}</code>
          </pre>
        </div>
      )}
      {msg && (
        <div className="message-content">
          <Markdown>{msg}</Markdown>
        </div>
      )}
      {data ? (
        <div className="data-content">{renderTable(data)}</div>
      ) : (
        <div className="message-content-greyed">
          <Markdown>There is no data output from the SQL generated.</Markdown>
        </div>
      )}
      {naturalLanguageAnswer && (
        <div className="natural-language-answer">
          <Markdown>{naturalLanguageAnswer}</Markdown>
        </div>
      )}
    </div>
  );
};

export default Message;
