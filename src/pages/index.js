import clsx from 'clsx';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import Heading from '@theme/Heading';
import styles from './index.module.css';

const highlights = [
  {
    title: '技术博客',
    description: '沉淀项目复盘、工程实践、源码阅读和学习过程。'
  },
  {
    title: '知识笔记',
    description: '把零散知识整理成可持续更新的体系。'
  },
  {
    title: '个人项目',
    description: '展示正在构建、实验和迭代的作品。'
  }
];

function Highlight({title, description}) {
  return (
    <article className={styles.highlight}>
      <h2>{title}</h2>
      <p>{description}</p>
    </article>
  );
}

export default function Home() {
  return (
    <Layout
      title="个人技术主页"
      description="黄振华的个人技术主页与博客">
      <main>
        <section className={styles.hero}>
          <div className="container">
            <p className={styles.eyebrow}>Personal Tech Site</p>
            <Heading as="h1" className={styles.title}>
              黄振华
            </Heading>
            <p className={styles.subtitle}>
              这里记录技术学习、工程实践、项目复盘，以及持续成长的轨迹。
            </p>
            <div className={styles.actions}>
              <Link className={clsx('button button--primary button--lg', styles.action)} to="/blog">
                阅读博客
              </Link>
              <Link className={clsx('button button--secondary button--lg', styles.action)} to="/notes/intro">
                查看笔记
              </Link>
            </div>
          </div>
        </section>

        <section className={styles.section}>
          <div className={clsx('container', styles.grid)}>
            {highlights.map((props) => (
              <Highlight key={props.title} {...props} />
            ))}
          </div>
        </section>
      </main>
    </Layout>
  );
}

