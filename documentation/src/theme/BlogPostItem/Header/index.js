import React from "react";
import Link from "@docusaurus/Link";
import { useLocation } from "@docusaurus/router";
import BlogPostItemHeader from "@theme-original/BlogPostItem/Header";

export default function BlogPostPageWrapper(props) {
  const location = useLocation();
  const isBlogPostPage = location.pathname.split("/").length > 3;
  return (
    <>
      {isBlogPostPage && (
        <Link
          to='/'
          style={{ display: "flex", alignItems: "center", marginBottom: 20 }}
        >
          <svg
            xmlns='http://www.w3.org/2000/svg'
            fill='none'
            viewBox='0 0 24 24'
            strokeWidth={2}
            stroke='currentColor'
            className='w-6 h-6'
            style={{ height: 24, marginRight: 4 }}
          >
            <path
              strokeLinecap='round'
              strokeLinejoin='round'
              d='M6.75 15.75L3 12m0 0l3.75-3.75M3 12h18'
            />
          </svg>
          <h3 style={{ margin: 0 }}>Return to docs</h3>
        </Link>
      )}
      <BlogPostItemHeader {...props} />
    </>
  );
}
