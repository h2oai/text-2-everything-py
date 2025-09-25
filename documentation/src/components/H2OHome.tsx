import React from 'react';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Link from '@docusaurus/Link';
import Icon from '@mui/material/Icon';
import defaultAppBanner from '@site/static/img/default_app_banner.png';
import styles from './home.module.css';

interface ItemObject {
  label: string;
  to?: string;
  href?: string;
}

interface SubsectionObject {
  title: string;
  subtitle?: string;
  icon?: string;
  items: ItemObject[];
}

interface CategoryProps {
  title: string;
  sections: SectionObject[];
}

interface SectionObject {
  title?: string;
  subsections?: SubsectionObject[];
}

let appBanner;
try {
  const customAppLogo = require('@site/static/img/app_banner.png');
  if (customAppLogo) appBanner = customAppLogo.default;
} catch (error) {
  console.log('Custom app logo not found, using default app logo instead.');
  appBanner = defaultAppBanner;
}

function Group(props: SubsectionObject) {
  const renderItems = props.items && props.items.length > 0;
  return (
    <div className={styles.group}>
      <div className={styles.groupContent}>
        <h4 className={styles.groupTitle}>
          {props.icon && <Icon className={styles.groupTitleIcon}>{props.icon}</Icon>}
          {props.title}
        </h4>
        {props.subtitle && <p>{props.subtitle}</p>}
        <ul className='links'>
          {renderItems &&
            props.items.map((item) => (
              <li key={item.label}>
                <Link to={item?.to} href={item?.href}>
                  {item.label}
                </Link>
              </li>
            ))}
        </ul>
      </div>
    </div>
  );
}

export function Category({ title, sections }: CategoryProps) {
  return (
    <div>
      <h3>{title}</h3>
      {(sections || []).map((section) => (
        <Section key={section?.title || section?.subsections?.length} {...section} />
      ))}
    </div>
  );
}

export function Section(props: SectionObject) {
  const id = props.title ? props.title.replaceAll(' ', '-').toLowerCase() : 'card-section';
  const renderSubsections = props.subsections && props.subsections.length > 0;
  return (
    <section className={styles.sections} id={id}>
      {props.title && <h2 className={styles.sectionTitle}>{props.title}</h2>}
      <div className='row'>{renderSubsections && props.subsections.map((subsection) => <Group key={subsection.title} {...subsection} />)}</div>
    </section>
  );
}

function H2OHome(props: { title?: string; description?: string; sections?: SectionObject[] }) {
  const context = useDocusaurusContext();
  const title = props.title || context?.siteConfig?.title;
  return (
    <>
      <header className={styles.header}>
        <img src={appBanner} alt='Header banner' className={styles.headerImage} />
        <div className={styles.headerWords}>
          <h2 className={styles.docsLabel}>Documentation</h2>
          <h1 className={styles.headerTitle}>{title}</h1>
          {props.description && <p className={styles.headerDescription}>{props.description}</p>}
        </div>
      </header>
      <main>
        {(props.sections || []).map((section) => (
          <Section key={section?.title || section?.subsections?.length} {...section} />
        ))}
      </main>
    </>
  );
}

export default H2OHome;
