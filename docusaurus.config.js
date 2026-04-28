// @ts-check

const config = {
  title: '黄振华',
  tagline: '个人技术主页与博客',
  favicon: 'img/favicon.svg',

  url: 'https://huangzhenhua111.github.io',
  baseUrl: '/',

  organizationName: 'huangzhenhua111',
  projectName: 'huangzhenhua111.github.io',
  trailingSlash: false,

  onBrokenLinks: 'throw',
  markdown: {
    hooks: {
      onBrokenMarkdownLinks: 'warn'
    }
  },

  i18n: {
    defaultLocale: 'zh-CN',
    locales: ['zh-CN']
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.js',
          routeBasePath: 'notes'
        },
        blog: {
          showReadingTime: true,
          blogTitle: '技术博客',
          blogDescription: '记录工程实践、学习笔记与思考',
          postsPerPage: 10,
          onUntruncatedBlogPosts: 'ignore'
        },
        theme: {
          customCss: './src/css/custom.css'
        }
      }
    ]
  ],

  themeConfig: {
    image: 'img/social-card.svg',
    navbar: {
      title: '黄振华',
      logo: {
        alt: '黄振华',
        src: 'img/favicon.svg'
      },
      items: [
        {to: '/blog', label: '博客', position: 'left'},
        {to: '/notes/intro', label: '笔记', position: 'left'},
        {
          href: 'https://github.com/huangzhenhua111',
          label: 'GitHub',
          position: 'right'
        }
      ]
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: '内容',
          items: [
            {label: '博客', to: '/blog'},
            {label: '笔记', to: '/notes/intro'}
          ]
        },
        {
          title: '社交',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/huangzhenhua111'
            }
          ]
        }
      ],
      copyright: `Copyright © ${new Date().getFullYear()} 黄振华`
    },
    prism: {
      additionalLanguages: ['bash', 'json']
    }
  }
};

export default config;
