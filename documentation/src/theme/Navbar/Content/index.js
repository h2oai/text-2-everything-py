import React from "react";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import { useThemeConfig } from "@docusaurus/theme-common";
import { useNavbarMobileSidebar } from "@docusaurus/theme-common/internal";
import Link from "@docusaurus/Link";
import NavbarItem from "@theme/NavbarItem";
import NavbarColorModeToggle from "@theme/Navbar/ColorModeToggle";
import SearchBar from "@theme/SearchBar";
import NavbarMobileSidebarToggle from "@theme/Navbar/MobileSidebar/Toggle";
import NavbarLogo from "@theme/Navbar/Logo";
import styles from "./styles.module.css";
import dropdownSchemas from "./dropdownSchemas";

function NavbarContentLayout({ left, right }) {
  return (
    <div className='navbar__inner'>
      <div className='navbar__items'>{left}</div>
      <div className='navbar__items navbar__items--right'>{right}</div>
    </div>
  );
}
export default function NavbarContent() {
  const context = useDocusaurusContext();
  const versions =
    context?.globalData?.["docusaurus-plugin-content-docs"]?.default?.versions;

  const mobileSidebar = useNavbarMobileSidebar();
  const navbarItems = useThemeConfig().navbar.items;
  const versionDropdownProps = navbarItems.find(
    (item) => item.type === "docsVersionDropdown"
  );

  const showVersionsDropdown =
    versions && versions.length > 1 && versionDropdownProps;
  const showVersionLabel =
    versions && versions.length === 1 && !showVersionsDropdown;
  const oldVersionsHref = context.siteConfig.customFields?.oldVersionsHref;
  const dropdownItemsAfter = oldVersionsHref
    ? [
        {
          to: oldVersionsHref,
          label: "Previous documentation versions",
        },
      ]
    : [];

  return (
    <NavbarContentLayout
      left={
        <>
          {!mobileSidebar.disabled && <NavbarMobileSidebarToggle />}
          <NavbarLogo />
          <div className={styles.navbarItems}>
            {dropdownSchemas.map((schema) => (
              <NavbarItem
                type='dropdown'
                key={schema.label}
                label={schema.label}
                items={schema.items}
              />
            ))}
          </div>
        </>
      }
      right={
        <>
          {showVersionsDropdown && (
            <NavbarItem
              {...versionDropdownProps}
              dropdownItemsAfter={dropdownItemsAfter}
            />
          )}
          {showVersionLabel && (
            <span className={styles.versionLabel}>{versions[0]?.label}</span>
          )}
          <SearchBar />
          <div className={styles.navbarButtons}>
            <Link to='https://h2o.ai/platform/ai-cloud/'>
              <button className='button navbar-button navbar-button--primary'>
                Learn More
              </button>
            </Link>
            <Link to='https://h2o.ai/demo/'>
              <button className='button navbar-button navbar-button--secondary'>
                Request a Demo
              </button>
            </Link>
          </div>
          <NavbarColorModeToggle className={styles.colorModeToggle} />
        </>
      }
    />
  );
}
