import clsx from 'clsx';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import Heading from '@theme/Heading';
import styles from './index.module.css';

const highlights = [
  {
    title: 'AI Agent',
    description: '记录 Agent workflow、多智能体系统、工具调用和工程化实践。'
  },
  {
    title: '项目复盘',
    description: '沉淀开源贡献、论文复现、评测分析和 bad case 归因。'
  },
  {
    title: '学习笔记',
    description: '整理 Python 后端、RAG、MCP、LangGraph、系统基础等内容。'
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
              北邮计算机硕士拟入学，关注 AI Agent、Multi-Agent Systems、Agent Evaluation 与 LLM 应用工程化。

              这里记录我的开源贡献、项目复盘、工程实践和学习笔记。
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

