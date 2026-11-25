import type { GovernmentService } from "../../types/domain";
import { Link } from "react-router-dom";
import Badge from "../common/Badge";
function ServiceCard({service,icon="▤"}: { service: GovernmentService; icon?: string }){return <Link to={service.status==="متاح"?"/services/"+service.id:"/services"} className="service-card"><div className="service-icon">{icon}</div><div className="service-meta"><Badge kind={service.status==="متاح"?"verified":"muted"}>{service.status==="متاح"?"دليل تجريبي متاح":"قريبًا"}</Badge><span>{service.cat}</span></div><h3>{service.name}</h3><p>{service.desc}</p><span className="card-link">التفاصيل ←</span></Link>}
export default ServiceCard;
