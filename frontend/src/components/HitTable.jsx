import DecisionBadge from "./DecisionBadge.jsx";

export default function HitTable({ hits, phaseLabel }) {
  if (!hits?.length) return null;

  return (
    <div className="table-wrap">
      <table className="table">
        <thead>
          <tr>
            {phaseLabel && <th>Phase</th>}
            <th>Rule</th>
            <th>Category</th>
            <th>Severity</th>
            <th>Matched</th>
          </tr>
        </thead>
        <tbody>
          {hits.map((hit) => (
            <tr key={`${phaseLabel || ""}-${hit.rule_id}-${hit.matched_text}`}>
              {phaseLabel && <td>{phaseLabel}</td>}
              <td>{hit.rule_name}</td>
              <td>{hit.category}</td>
              <td>
                <DecisionBadge decision={hit.severity} />
              </td>
              <td className="mono cell-clip" title={hit.matched_text}>
                {hit.matched_text}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}