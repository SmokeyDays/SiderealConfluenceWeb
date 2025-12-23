import { type GlobalThemeOverrides } from 'naive-ui';

// 1. 定义调色板 (方便在 JS/TS 中复用颜色逻辑)
export const sidConPalette = {
  primary: '#00d4ff',        // 核心青色 (Core Cyan)
  primaryHover: '#5ce1ff',   // 高亮青
  primaryPressed: '#009bbd', // 按下深青
  primarySuppl: 'rgba(0, 212, 255, 0.15)', // 辅助底色

  info: '#b0056cff',           // 信息色
  success: '#00ff9d',        // 霓虹绿 (Neon Green)
  warning: '#f2c94c',        // 琥珀黄 (Amber)
  error: '#ff3b3b',          // 警报红 (Alert Red)

  bgBase: '#050a14',         // 深空黑 (Deep Space)
  bgCard: 'rgba(0, 20, 40, 0.85)', // 半透明面板背景
  bgOverlay: 'rgba(0, 10, 20, 0.95)', // 弹窗背景
  
  textBase: '#e0e0e0',       // 主文本
  textDim: 'rgba(255, 255, 255, 0.5)', // 次级文本
  
  border: 'rgba(0, 212, 255, 0.3)', // 默认边框
  borderStrong: 'rgba(0, 212, 255, 0.6)', // 强调边框
};

// 2. 定义字体栈 (优先使用本地科幻字体)
const fontStack = '"Orbitron", "Share Tech Mono", "Smiley Sans", "Microsoft YaHei", "PingFang SC", sans-serif';
const titleFontStack = '"Orbitron", "Share Tech Mono", sans-serif';

function hexToRgba(hex: string, alpha: number): string {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

const createButtonVariant = (color: string, typeSuffix: string = '') => {
  const suffix = typeSuffix;
  return {
    // 1. 文本颜色：常态为彩色，悬浮/按下为白色
    [`textColor${suffix}`]: color,
    [`textColorHover${suffix}`]: '#ffffff',
    [`textColorPressed${suffix}`]: '#ffffff',
    [`textColorFocus${suffix}`]: color,
    [`textColorDisabled${suffix}`]: color,
    
    [`textColorText${suffix}`]: color,
    [`textColorTextHover${suffix}`]: '#ffffff',
    [`textColorTextPressed${suffix}`]: '#ffffff',
    [`textColorTextFocus${suffix}`]: color,
    [`textColorTextDisabled${suffix}`]: color,

    // 2. 边框颜色：始终有色，保持扁平硬朗感
    [`border${suffix}`]: `1px solid ${color}`,
    [`borderHover${suffix}`]: `1px solid ${color}`,
    [`borderPressed${suffix}`]: `1px solid ${color}`, // 或者稍微加深
    [`borderFocus${suffix}`]: `1px solid ${color}`,
    [`borderDisabled${suffix}`]: `1px solid ${color}`,

    // 3. 背景颜色：常态透明(幽灵)，悬浮/按下出现半透明色块
    [`color${suffix}`]: color, 
    [`colorHover${suffix}`]: hexToRgba(color, 0.15),
    [`colorPressed${suffix}`]: hexToRgba(color, 0.3),
    [`colorFocus${suffix}`]: hexToRgba(color, 0.15),
    [`colorDisabled${suffix}`]: color,
    
    [`rippleColor${suffix}`]: color, 
  };
};

export const sidConThemeOverrides: GlobalThemeOverrides = {
  common: {
    // 基础色
    primaryColor: sidConPalette.primary,
    primaryColorHover: sidConPalette.primaryHover,
    primaryColorPressed: sidConPalette.primaryPressed,
    primaryColorSuppl: sidConPalette.primarySuppl,
    
    infoColor: sidConPalette.info,
    successColor: sidConPalette.success,
    warningColor: sidConPalette.warning,
    errorColor: sidConPalette.error,

    // 背景与文字
    bodyColor: sidConPalette.bgBase,
    cardColor: sidConPalette.bgCard,
    modalColor: sidConPalette.bgOverlay,
    popoverColor: sidConPalette.bgOverlay,
    textColorBase: sidConPalette.textBase,
    textColor1: sidConPalette.textBase,
    textColor2: sidConPalette.textBase,
    textColor3: sidConPalette.textDim,

    // 字体与圆角
    fontFamily: fontStack,
    fontFamilyMono: fontStack,
    borderRadius: '0px',       // 【关键】去圆角
    borderRadiusSmall: '0px',
    
    // 全局边框
    borderColor: sidConPalette.border,
  },
  
  // --- 组件级定制 ---
  
  Button: {
    // 按钮更加扁平化，强调边框
    border: `1px solid ${sidConPalette.border}`,
    borderHover: `1px solid ${sidConPalette.primary}`,
    borderPressed: `1px solid ${sidConPalette.primaryPressed}`,
    borderFocus: `1px solid ${sidConPalette.primary}`,
    
    textColor: sidConPalette.primary,
    textColorBase: sidConPalette.primary,
    textColorHover: '#fff',
    textColorPressed: '#fff',
    textColorFocus: sidConPalette.primary,
    textColorDisabled: sidConPalette.primary,

    colorOpacitySecondary: 0, 
    colorSecondaryHover: 'rgba(0, 212, 255, 0.15)',
    colorSecondaryPressed: 'rgba(0, 212, 255, 0.3)',


    fontWeight: 'bold',
    fontFamily: titleFontStack,
    
    ...createButtonVariant(sidConPalette.primary, ''),
    ...createButtonVariant(sidConPalette.primary, 'Primary'),
    ...createButtonVariant(sidConPalette.info, 'Info'),
    ...createButtonVariant(sidConPalette.success, 'Success'),
    ...createButtonVariant(sidConPalette.warning, 'Warning'),
    ...createButtonVariant(sidConPalette.error, 'Error'),
  },
  
  Card: {
    // 卡片像一个玻璃面板
    color: sidConPalette.bgCard,
    borderColor: sidConPalette.border,
    textColor: sidConPalette.textBase,
    titleTextColor: sidConPalette.primary,
    titleFontWeight: 'bold',
    fontFamily: fontStack,
  },
  
  Input: {
    // 输入框像数据录入终端
    color: 'rgba(0, 0, 0, 0.3)',
    colorFocus: 'rgba(0, 10, 20, 0.5)',
    border: `1px solid ${sidConPalette.border}`,
    borderHover: `1px solid ${sidConPalette.primary}`,
    borderFocus: `1px solid ${sidConPalette.primary}`,
    boxShadowFocus: `0 0 8px rgba(0, 212, 255, 0.3)`,
    textColor: sidConPalette.textBase,
    caretColor: sidConPalette.primary,
  },
  
  Select: {
    peers: {
      InternalSelection: {
        color: 'rgba(0, 0, 0, 0.3)',
        border: `1px solid ${sidConPalette.border}`,
        borderHover: `1px solid ${sidConPalette.primary}`,
        borderActive: `1px solid ${sidConPalette.primary}`,
        textColor: sidConPalette.textBase,
      },
      InternalSelectMenu: {
        color: sidConPalette.bgOverlay,
        // border: `1px solid ${sciFiPalette.border}`,
        optionTextColor: sidConPalette.textBase,
        optionTextColorActive: sidConPalette.primary,
        optionCheckColor: sidConPalette.primary,
      }
    }
  },

  DataTable: {
    // 表格像数据清单
    thColor: 'rgba(0, 212, 255, 0.1)', // 表头淡青色背景
    thTextColor: sidConPalette.primary,
    thFontWeight: 'bold',
    tdColor: 'transparent',
    tdTextColor: sidConPalette.textBase,
    borderColor: sidConPalette.border,
    tdColorHover: 'rgba(0, 212, 255, 0.05)',
  },
  
  Dialog: {
    // 弹窗像系统警告框
    color: sidConPalette.bgOverlay,
    border: `1px solid ${sidConPalette.primary}`,
    titleTextColor: sidConPalette.primary,
    textColor: sidConPalette.textBase,
    iconColor: sidConPalette.primary,
    headerBorderBottom: `1px solid ${sidConPalette.border}`,
  },

  Alert: {
    color: 'rgba(0, 20, 40, 0.6)',
    border: `1px solid ${sidConPalette.border}`,
    titleTextColor: sidConPalette.primary,
    contentTextColor: sidConPalette.textBase,
  },

  Tooltip: {
    color: 'rgba(0, 10, 20, 0.95)',
    textColor: sidConPalette.primary,
    border: `1px solid ${sidConPalette.border}`,
  },
  
  Divider: {
    color: sidConPalette.border,
  },
  
  Typography: {
    headerFontColor: sidConPalette.primary,
    headerFontFamily: titleFontStack,
  }
};