import React from "react";
import Link from "@docusaurus/Link";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import { useLocation } from "@docusaurus/router";
import MDXContent from "@theme-original/MDXContent";
import Admonition from "@theme/Admonition";

export default function MDXContentWrapper(props) {
  const docusaurusContext = useDocusaurusContext();
  const { pathname } = useLocation();

  const version = docusaurusContext?.siteMetadata?.siteVersion;
  const applicationName = docusaurusContext?.siteConfig?.title;
  const assignee =
    docusaurusContext?.siteConfig?.customFields?.feedbackAssignee;
  const labels = docusaurusContext?.siteConfig?.customFields?.feedbackLabels;
  const labelsParam = labels ? `labels=${labels.join("+")}&` : "";

  const showFeedbackWidget = pathname && !pathname.includes("/blog");
  if (!showFeedbackWidget) return <MDXContent {...props} />;

  return (
    <>
      <MDXContent {...props} />
      <hr />
      <Admonition title='Feedback' type='note'>
        <ul>
          <li>
            <Link
              to={`https://github.com/h2oai/docs-issues-requests/issues/new?assignees=${assignee}&${labelsParam}body=%23%23%23%20Documentation%20issue%2Frequest%0A%0A%3C!--%20Please%20provide%20a%20clear%20and%20concise%20description%20of%20the%20documentation%20issue%2Frequest%20--%3E%0A%0A%23%23%23%20Additional%20context%0A%0A%3C!--%20Please%20add%20any%20other%20context%20about%20the%20issue%2Frequest%20here%20(e.g.%2C%20images)%20--%3E%0A%0A%23%23%23%20Page%20details%20%0A%0A-%20Application%20name%3A%20${applicationName}%0A-%20Application%20version%3A%20${version}%0A-%20Page%20title%3A%20${pathname}%20&title=%5BHAIC-APP%5D`}
            >
              Submit and view feedback for this page
            </Link>
          </li>
          <li>
            {`Send feedback about ${applicationName} to `}
            <Link to='mailto:cloud-feedback@h2o.ai'>cloud-feedback@h2o.ai</Link>
          </li>
        </ul>
      </Admonition>
    </>
  );
}
