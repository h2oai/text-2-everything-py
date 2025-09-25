import { themes } from 'prism-react-renderer';

const config = {
  title: "Text2Everything SDK",
  tagline: "Transform natural language into SQL queries with enterprise-grade reliability",
  url: "https://h2oai.github.io",
  baseUrl: "/text-2-everything-py/",
  onBrokenLinks: "throw",
  onBrokenMarkdownLinks: "warn",
  favicon: "img/favicon.ico",
  organizationName: "h2oai", 
  projectName: "text-2-everything-py",
  deploymentBranch: "gh-pages", 
  trailingSlash: false,
  i18n: {
    defaultLocale: "en",
    locales: ["en"],
  },
  presets: [
    [
      "classic",
      {
        blog: false,
        docs: {
          routeBasePath: "/",
          sidebarPath: require.resolve("./sidebars.js"),
          showLastUpdateTime: true,
          showLastUpdateAuthor: true,
          includeCurrentVersion: true,
          disableVersioning: false,
          lastVersion: "current",
          versions: {},
        },
        theme: {
          customCss: require.resolve("./src/css/custom.css"),
        },
        sitemap: {
          lastmod: 'date',
          changefreq: 'weekly',
          priority: 0.5,
          ignorePatterns: [],
          filename: 'sitemap.xml',
          createSitemapItems: async ({ defaultCreateSitemapItems, routes, ...other }) => {
            const fs = require('fs');
            const path = require('path');
            const { execSync } = require('child_process');
            
            const patchSourceFilePath = (route) => {
              if (route.metadata?.sourceFilePath) {
                const originalPath = route.metadata.sourceFilePath;
                
                // Try multiple path resolutions for different deployment scenarios
                const pathsToTry = [
                  `../${originalPath}`, // Original logic for local development
                  originalPath, // Direct path for some CI/CD scenarios
                  path.resolve(process.cwd(), originalPath), // Absolute path resolution
                  path.resolve(process.cwd(), '..', originalPath), // One level up resolution
                ];
                
                // Find the first existing path
                let resolvedPath = null;
                for (const testPath of pathsToTry) {
                  try {
                    if (fs.existsSync(testPath)) {
                      resolvedPath = testPath;
                      break;
                    }
                  } catch (e) {
                    // Continue to next path if this one fails
                    continue;
                  }
                }
                
                // Use the resolved path if found, otherwise keep original behavior
                if (resolvedPath) {
                  route.metadata.sourceFilePath = resolvedPath;
                } else {
                  // Fallback to original logic if no path is found
                  route.metadata.sourceFilePath = `../${originalPath}`;
                }
              }
              // if the routes are nested, like in the case of `docusaurus-plugin-content-docs` plugin, traverse them recursively
              route.routes?.forEach(patchSourceFilePath);
            };
            
            // Apply path patches
            routes.forEach(patchSourceFilePath);
            
            // Generate sitemap items with default logic first
            const userCreateSitemapItems = undefined;
            let items;
            if (userCreateSitemapItems) {
              items = await userCreateSitemapItems({
                defaultCreateSitemapItems,
                routes,
                ...other,
              });
            } else {
              items = await defaultCreateSitemapItems({
                routes,
                ...other,
              });
            }
            
            // Post-process items to fix lastmod dates
            for (const item of items) {
              try {
                // Find corresponding route
                const route = routes.find(r => {
                  const routeUrl = r.path?.replace(/\/$/, '') || '';
                  const itemUrl = item.url?.replace(/\/$/, '') || '';
                  return routeUrl === itemUrl || itemUrl.includes(routeUrl);
                });
                
                if (route?.metadata?.sourceFilePath) {
                  const sourceFile = route.metadata.sourceFilePath;
                  
                  // Try to get git commit time first
                  try {
                    const gitCommand = `git log -1 --format="%ai" -- "${sourceFile}"`;
                    const gitDate = execSync(gitCommand, { 
                      encoding: 'utf8', 
                      cwd: path.dirname(sourceFile),
                      timeout: 5000 
                    }).trim();
                    
                    if (gitDate) {
                      item.lastmod = new Date(gitDate).toISOString();
                      continue;
                    }
                  } catch (gitError) {
                    // Git command failed, try filesystem mtime
                  }
                  
                  // Fallback to filesystem modification time
                  try {
                    const stats = fs.statSync(sourceFile);
                    item.lastmod = stats.mtime.toISOString();
                  } catch (fsError) {
                    // Keep existing lastmod or use current time
                    if (!item.lastmod) {
                      item.lastmod = new Date().toISOString();
                    }
                  }
                }
              } catch (error) {
                // Keep existing lastmod if any error occurs
                if (!item.lastmod) {
                  item.lastmod = new Date().toISOString();
                }
              }
            }
            
            return items;
          },
        },
      },
    ],
  ],
  stylesheets: ["https://fonts.googleapis.com/icon?family=Material+Icons"],
  themeConfig:
    ({
      navbar: {
        title: "Text2Everything SDK",
        logo: {
          alt: "H2O.ai logo",
          src: "img/h2oai.png",
          href: "https://h2o.ai/",
        },
        items: [
          { type: 'docsVersionDropdown', position: 'right' },
        ],
      },
      footer: {
        style: "dark",
        links: [
          {
            title: "About us",
            items: [
              {
                label: "H2O.AI",
                href: "https://h2o.ai/",
              },
              {
                label: "Contact us",
                href: "https://h2o.ai/company/contact-us/",
              },
            ],
          },
          {
            title: "Legal",
            items: [
              {
                label: "Privacy policy",
                href: "https://h2o.ai/legal/privacy/",
              },
              {
                label: "Compliance & responsible AI",
                href: "https://h2o.ai/insights/responsible-ai/",
              },
            ],
          },
          {
            title: "Community",
            items: [
              {
                label: "Twitter",
                href: "https://twitter.com/h2oai",
              },
              {
                label: "LinkedIn",
                href: "https://www.linkedin.com/company/h2oai",
              },
              {
                label: "YouTube",
                href: "https://www.youtube.com/c/H2Oai",
              },
            ],
          },
        ],
        copyright: `Copyright © 2025 <a href='https://h2o.ai' style='color:#FFE600'>H2O.ai</a>, Inc.`,
      },
      prism: {
        theme: themes.github,
        darkTheme: themes.dracula,
      },
      algolia: {
        appId: "ADXS57JGWZ",
        // Public API key: it is safe to commit it
        apiKey: "307af4d33ed2092dccfa145365fd2370",
        indexName: "dev_docs_omnisearch",
        // Version facets vary from site to site, so contextual search screws up results
        contextualSearch: false,
        externalUrlRegex: ".*",
      },
      metadata: [{ name: "sitename", content: "Text2Everything SDK" }],
    }),
  plugins: [
    [
      "@docusaurus/plugin-client-redirects",
      {
        redirects: [
          {
            to: "/",
            from: ["/latest", "/latest/home"],
          },
        ],
      },
    ],
  ],
  customFields: {
    feedbackAssignee: "5675sp",
  }
};

module.exports = config;
  