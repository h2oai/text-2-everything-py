module.exports = {
  defaultSidebar: [
    "index",
    {
      type: 'category',
      label: 'Get Started',
      link: { type: 'doc', id: 'get-started' },
      items: [
        'quickstart',
        'installation',
        'configuration',
      ],
    },
    {
      "Quick Start Guides": [
        "quick-start/README",
        "quick-start/five-minute-start",
        "quick-start/complete-example",
        "quick-start/developer-starter-guide",
        "quick-start/quick-reference",
      ],
    },
    {
      "Guides": [
        "guides/projects",
        "guides/contexts",
        "guides/schema_metadata",
        "guides/golden_examples",
        "guides/connectors",
        "guides/chat_sessions",
        "guides/chat",
        "guides/chat_presets",
        "guides/executions",
        "guides/feedback",
        "guides/custom_tools",
        "guides/concurrency",
      ],
    },
    {
      "How To": [
        "how-to/bulk_operations",
        "how-to/jupyter",
        "how-to/validation",
      ],
    },
    {
      "Advanced": [
        "high-concurrency-testing",
        "migrations",
        "troubleshooting",
      ],
    },
  ],
};