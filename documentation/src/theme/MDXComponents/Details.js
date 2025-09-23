import React from "react";
import Details from "@theme/Details";
export default function MDXDetails(props) {
  const items = React.Children.toArray(props.children);
  // Split summary item from the rest to pass it as a separate prop to the
  // Details theme component
  const summary = items.find(
    (item) => React.isValidElement(item) && item.props?.mdxType === "summary"
  );
  const children = <>{items.filter((item) => item !== summary)}</>;
  return (
    // Swizzle: Pass "open" prop to set accordion open by default
    <Details {...props} open summary={summary}>
      {children}
    </Details>
  );
}
