import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

const config: Config = {
  title: 'saturday',
  tagline: 'An app designed to scrape science publication metadata from various sources ',
  favicon: 'img/favicon.ico',

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  // Set the production url of your site here
  url: 'https://dpago.dev',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/saturday',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'bonk-dev', // Usually your GitHub org/user name.
  projectName: 'saturday', // Usually your repo name.

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'pl',
    locales: ['pl'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          routeBasePath: '/'
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      },
    ],
  ],

  themeConfig: {
    // Replace with your project's social card
    image: 'img/saturday-social-card.jpg',
    navbar: {
      title: 'saturday',
      logo: {
        alt: 'saturday logo',
        src: 'img/logo.svg',

      },
      items: [
        {
          href: 'https://github.com/bonk-dev/saturday',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Dokumentacja',
          items: [
            {
              label: 'Instrukcja obsługi',
              to: '/category/wstepna-konfiguracja',
            },
            {
              label: 'Opis projektu',
              to: '/category/opis-projektu',
            },
            {
              label: 'Podsumowanie',
              to: '/podsumowanie',
            },
          ],
        },
        {
          title: 'Więcej',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/bonk-dev/saturday',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Dawid Pągowski, Maciej Czaicki. Dokumentacja stworzona za pomocą Docusaurusa.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  },
  markdown: {
    mermaid: true
  },
  themes: ['@docusaurus/theme-mermaid']
};

export default config;
