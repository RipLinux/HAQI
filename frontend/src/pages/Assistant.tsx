import { useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import Shell from "../components/layout/Shell";
import Badge from "../components/common/Badge";
import { sampleQuestions, disclaimer } from "../data/services";
import { sendChat } from "../services/api";
import type { ChatResponse } from "../types/api";

type UiMessage = {
  role: "user" | "bot";
  text: string;
  response?: ChatResponse;
};

function Assistant() {
  const [params] = useSearchParams();

  const [value, setValue] = useState(params.get("q") || "");
  const [messages, setMessages] = useState<UiMessage[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const send = async (text = value) => {
    if (!text.trim() || loading) return;

    const question = text.trim();

    setValue("");
    setError("");

    setMessages((previous) => [
      ...previous,
      { role: "user", text: question },
    ]);

    setLoading(true);

    try {
      const response = await sendChat({
        question,
        user_id: "guest_user",
        session_id: sessionId,
        service_category: null,
      });

      setSessionId(response.session_id);

      setMessages((previous) => [
        ...previous,
        {
          role: "bot",
          text: response.answer,
          response,
        },
      ]);
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : "حدث خطأ غير متوقع";

      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const newConversation = () => {
    setMessages([]);
    setSessionId(null);
    setValue("");
    setError("");
  };

  return (
    <Shell>
      <main className="page wrap assistant-page">
        <div className="page-intro centered">
          <Badge>المساعد الذكي للخدمات الحكومية</Badge>

          <h1>اسأل حقي</h1>

          <p>
            اسألني عن الخدمات والإجراءات الحكومية، وسأساعدك في الوصول
            للمعلومات والمصادر الرسمية.
          </p>
        </div>

        <div className="chat-shell">
          <div className="chat-head">
            <span className="assistant-avatar">ح</span>

            <div>
              <b>حقي — المساعد الذكي</b>

              <small>
                <i></i>{" "}
                {loading
                  ? "جاري التفكير..."
                  : "متاح للمساعدة"}
              </small>
            </div>

            <button type="button" onClick={newConversation}>
              محادثة جديدة ↻
            </button>
          </div>

          <div className="chat-body">
            {messages.length === 0 ? (
              <div className="welcome-chat">
                <span className="assistant-avatar big">ح</span>

                <h2>
                  أهلًا! اسألني عن الخدمات الحكومية
                </h2>

                <p>
                  زي تجديد البطاقة، شهادة الميلاد، أو القيد العائلي.
                  اختار سؤال من تحت أو اكتب سؤالك.
                </p>

                <div className="suggestions">
                  {sampleQuestions.map((question) => (
                    <button
                      key={question}
                      type="button"
                      disabled={loading}
                      onClick={() => send(question)}
                    >
                      {question}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              messages.map((message, index) => {
                const result = message.response;

                const showStructuredGuidance =
                  message.role === "bot" &&
                  result?.decision_type === "answered" &&
                  result.structured_guidance;

                return (
                  <div
                    key={index}
                    className={`message ${message.role}`}
                  >
                    {message.role === "bot" && (
                      <span className="assistant-avatar tiny">
                        ح
                      </span>
                    )}

                    <div className="bubble">
                      {!showStructuredGuidance && (
                        <p>{message.text}</p>
                      )}

                      {result?.decision_type ===
                        "clarification_needed" &&
                        result.clarification_options &&
                        result.clarification_options.length > 0 && (
                          <div className="suggestions">
                            <p>
                              اختاري الإجابة المناسبة:
                            </p>

                            {result.clarification_options.map(
                              (option) => (
                                <button
                                  key={option}
                                  type="button"
                                  disabled={loading}
                                  onClick={() => send(option)}
                                >
                                  {option}
                                </button>
                              ),
                            )}
                          </div>
                        )}

                      {showStructuredGuidance && (
                        <div className="guidance">
                          {result.structured_guidance
                            ?.specific_service && (
                            <p>
                              <strong>الخدمة:</strong>{" "}
                              {
                                result.structured_guidance
                                  .specific_service
                              }
                            </p>
                          )}

                          {result.structured_guidance
                            ?.procedural_steps &&
                            result.structured_guidance
                              .procedural_steps.length > 0 && (
                              <div>
                                <strong>
                                  خطوات الإجراء:
                                </strong>

                                <ol>
                                  {result.structured_guidance.procedural_steps.map(
                                    (step, i) => (
                                      <li key={i}>{step}</li>
                                    ),
                                  )}
                                </ol>
                              </div>
                            )}

                          {result.structured_guidance
                            ?.required_documents &&
                            result.structured_guidance
                              .required_documents.length > 0 && (
                              <div>
                                <strong>
                                  المستندات المطلوبة:
                                </strong>

                                <ul>
                                  {result.structured_guidance.required_documents.map(
                                    (doc, i) => (
                                      <li key={i}>{doc}</li>
                                    ),
                                  )}
                                </ul>
                              </div>
                            )}

                          {result.structured_guidance
                            ?.responsible_authority && (
                            <p>
                              <strong>الجهة المسؤولة:</strong>{" "}
                              {
                                result.structured_guidance
                                  .responsible_authority
                              }
                            </p>
                          )}

                          {result.structured_guidance
                            ?.fees_and_duration && (
                            <p>
                              <strong>الرسوم والمدة:</strong>{" "}
                              {
                                result.structured_guidance
                                  .fees_and_duration
                              }
                            </p>
                          )}

                          {(!result.citations ||
                            result.citations.length === 0) &&
                            result.structured_guidance
                              ?.reference_and_verification && (
                              <p>
                                <strong>
                                  المرجع وحالة التحقق:
                                </strong>{" "}
                                {
                                  result.structured_guidance
                                    .reference_and_verification
                                }
                              </p>
                            )}

                          {result.structured_guidance
                            ?.methodological_note && (
                            <small>
                              {
                                result.structured_guidance
                                  .methodological_note
                              }
                            </small>
                          )}
                        </div>
                      )}

                      {result?.decision_type === "safe_abstention" &&
                        result.evidence_validation?.abstention_reason &&
                        result.evidence_validation.abstention_reason.trim() !==
                          message.text.trim() && (
                          <div>
                            <small>
                              {result.evidence_validation.abstention_reason}
                            </small>
                          </div>
                        )}

                      {(!result?.citations ||
                        result.citations.length === 0) &&
                        result?.sources &&
                        result.sources.length > 0 && (
                          <div className="source-line">
                            <strong>المصادر:</strong>

                            <ul>
                              {result.sources.map(
                                (source, i) => (
                                  <li key={i}>{source}</li>
                                ),
                              )}
                            </ul>
                          </div>
                        )}

                      {result?.citations &&
                        result.citations.length > 0 && (
                          <div className="source-line">
                            <strong>
                              المراجع الرسمية:
                            </strong>

                            {result.citations.map(
                              (citation, i) => (
                                <p key={i}>
                                  {citation.title ||
                                    citation.doc_code}

                                  {citation.authority &&
                                    ` — ${citation.authority}`}

                                  {citation.original_url && (
                                    <>
                                      {" — "}

                                      <a
                                        href={
                                          citation.original_url
                                        }
                                        target="_blank"
                                        rel="noreferrer"
                                      >
                                        عرض المصدر ↗
                                      </a>
                                    </>
                                  )}

                                  {citation.verification_date && (
                                    <small>
                                      {" "}
                                      — تاريخ التحقق:{" "}
                                      {citation.verification_date}
                                    </small>
                                  )}
                                </p>
                              ),
                            )}
                          </div>
                        )}

                      {message.role === "bot" && (
                        <small>{disclaimer}</small>
                      )}
                    </div>
                  </div>
                );
              })
            )}

            {loading && (
              <div className="message bot">
                <span className="assistant-avatar tiny">
                  ح
                </span>

                <div className="bubble">
                  <p>
                    جاري البحث عن إجابة مناسبة...
                  </p>
                </div>
              </div>
            )}
          </div>

          {error && (
            <div className="panel">
              <p>
                تعذر الاتصال بالمساعد: {error}
              </p>

              <button
                type="button"
                onClick={() => send(value)}
              >
                إعادة المحاولة
              </button>
            </div>
          )}

          <form
            className="chat-input"
            onSubmit={(event) => {
              event.preventDefault();
              send();
            }}
          >
            <input
              value={value}
              onChange={(event) =>
                setValue(event.target.value)
              }
              placeholder="اكتب سؤالك بالعربي..."
              disabled={loading}
            />

            <button
              type="submit"
              disabled={loading || !value.trim()}
            >
              {loading ? "انتظر..." : "إرسال ←"}
            </button>
          </form>

          <p className="privacy-note">
            يتم إرسال سؤالك إلى خادم المساعد المحلي لمعالجته.
            لا تكتب بيانات شخصية مثل رقمك القومي.
          </p>
        </div>

        <div className="panel reading-help">
          <h3>إزاي تقرأ الإجابة؟</h3>

          <ul>
            <li>
              الإجابة مدعومة بالمعلومات المتاحة من مصادر النظام.
            </li>

            <li>
              لو محتاج توضيح، اختار الإجابة المناسبة عشان نكمل
              المحادثة.
            </li>

            <li>
              لو الأدلة غير كافية، حقي مش هيخمّن وهيبلغك بذلك.
            </li>

            <li>
              تقدر تراجع المصادر الرسمية من الروابط المرفقة
              بالإجابة.
            </li>
          </ul>
        </div>

        <div className="tool-links">
          <Link to="/services">دليل الخدمات</Link>

          <Link to="/document-check">
            فحص المستندات (تجريبي)
          </Link>

          <Link to="/sources">
            المصادر والموثوقية
          </Link>
        </div>
      </main>
    </Shell>
  );
}

export default Assistant;