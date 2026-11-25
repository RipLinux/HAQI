import { Link } from "react-router-dom";
import { disclaimer } from "../../data/services";

function Footer() {
  return (
    <footer className="footer">
      <div className="wrap footer-grid">
        <div>
          <Link className="brand light" to="/">
            <span className="brand-mark">ح</span>
            <span>
              <b>حقي</b>
              <small>HAQI</small>
            </span>
          </Link>

          <p>
            افهم حقك… وخطوتك الجاية. مساعد عربي يشرح الخدمات العامة في مصر
            بلغة بسيطة ويوجّهك للمصدر الرسمي.
          </p>
        </div>

        <div>
          <b>روابط</b>
          <Link to="/assistant">اسأل حقي</Link>
          <Link to="/services">دليل الخدمات</Link>
          <Link to="/document-check">فحص المستندات (تجريبي)</Link>
          <Link to="/sources">المصادر والموثوقية</Link>
        </div>

        <div>
          <b>تنبيه مهم</b>
          <p>{disclaimer}</p>
          <small>
            تُرسل الأسئلة إلى خادم المساعد لمعالجتها. يُرجى عدم إدخال بيانات
            شخصية مثل الرقم القومي.
          </small>
        </div>
      </div>

      <div className="wrap copyright">
        حقي · HAQI — نموذج عرض تجريبي
      </div>
    </footer>
  );
}

export default Footer;