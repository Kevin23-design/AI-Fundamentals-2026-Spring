import React, { useState, useEffect, useRef, useMemo } from 'react';
import { ChevronLeft, ChevronRight, Play, Pause, RotateCcw, Maximize, Github, Video, X, Link, MessageSquare, Send, Bot } from 'lucide-react';

// --- 常量配置 ---
const GRID_SIZE = 30;
const COLS = 20;
const ROWS = 14;
const CANVAS_WIDTH = COLS * GRID_SIZE;
const CANVAS_HEIGHT = ROWS * GRID_SIZE;
const OBSTACLE_COST = 255;
const NORMAL_COST = 1;
const NUM_PARTICLES = 60;

// --- 幻灯片内容数据 ---
const SLIDES = [
  {
    id: 1,
    title: "向量场群体寻路算法",
    subtitle: "Vector Field Pathfinding (Flow Field)",
    content: [
      "告别卡顿，实现海量单位的丝滑移动",
      "基于全局流动的寻路方案",
      "张子扬 10245102456 4.24"
    ],
    visualMode: "title"
  },
  {
    id: 2,
    title: "演示大纲",
    subtitle: "Agenda",
    content: [
      "第一部分：引入传统算法痛点展示",
      "第二部分：破局之法——向量场思想",
      "第三部分：构建热力图与生成向量场",
      "深入解析：双线性插值与分离避障",
      "优化改进：修复对角线物理穿模死锁",
      "理论对比：时空复杂度分析",
      "最终成果演示与资料开源"
    ],
    visualMode: "agenda"
  },
  {
    id: 3,
    title: "第一部分：引入与痛点展示",
    subtitle: "The Problem",
    content: [
      "应用场景：即时战略（RTS）、塔防或“类吸血鬼幸存者”等游戏中，存在大量单位需要进行寻路。",
      "痛点分析：传统的 A* 算法（A Star）在处理少量单位时极其精准。",
      "算力瓶颈：如果让成百上千个单位各自独立进行路径计算，会产生极高的性能消耗，导致群体拥挤、卡顿或极其不自然的移动表现。"
    ],
    visualMode: "problem"
  },
  {
    id: 4,
    title: "第二部分：破局之法——向量场算法",
    subtitle: "The Solution",
    content: [
      "概念说明：正式引入“向量场群体寻路算法”，也常称其为“流场寻路”（Flow Field Pathfinding）。",
      "核心思路转换：不再为每一个独立的个体计算从起点到终点的路径！",
      "全局视角：而是为“整个地图空间”计算出指向目标的流动趋势。让地图本身指引单位移动。"
    ],
    visualMode: "solution"
  },
  {
    id: 5,
    title: "第三部分：核心算法 BFS 实现",
    subtitle: "Implementation: Breadth-First Search",
    content: [
      "使用队列 (Queue) 从目标点向外层层扩散",
      "累加移动代价 (Cost) 构建距离场",
      "👉 右侧演示：观察 BFS 算法是如何探索未知区域并绕开障碍物的"
    ],
    code: `// BFS 扩散核心逻辑示意
const queue = [targetNode];
targetNode.cost = 0;

while (queue.length > 0) {
  const curr = queue.shift();
  
  for (const n of curr.neighbors) {
    if (n.isObstacle) continue;
    
    const newCost = curr.cost + moveCost;
    // 如果找到了更短的路径，则更新
    if (newCost < n.cost) {
      n.cost = newCost;
      queue.push(n);
    }
  }
}`,
    visualMode: "bfs_step"
  },
  {
    id: 6,
    title: "第三部分：步骤一 构建热力图",
    subtitle: "Step 1: Heatmap (Integration Field)",
    content: [
      "这就是刚刚 BFS 算法运行完毕后的最终结果。",
      "计算地图上每个网格到达终点的累积距离成本（Integration Cost）。",
      "遇到障碍物则绕行，最终生成一张覆盖全图的“热力图”。",
      "通过颜色深浅和数字，可以直观看到“高地势”和“低地势”。"
    ],
    visualMode: "heatmap"
  },
  {
    id: 7,
    title: "第三部分：步骤二 生成向量场",
    subtitle: "Step 2: Vector Field",
    content: [
      "根据热力图的成本差异，寻找方向。",
      "遍历每个网格，查看其相邻的 8 个网格的成本。",
      "计算出一个指向最低成本方向的向量（箭头）。",
      "由此构建出覆盖全图的向量场，就像是一张指引水流方向的地图。"
    ],
    visualMode: "vector"
  },
  {
    id: 8,
    title: "深入解析：双线性插值",
    subtitle: "Deep Dive: Bilinear Interpolation",
    content: [
      "网格中心：向量场实际上存储在每个网格的中心点。如果单位只读取所在网格的力，跨越网格时会产生生硬的“折线”转向。",
      "面积权重：计算单位距离周围 4 个网格中心点的位置比例（tx, ty）。",
      "二次混合：先在 X 轴插值，再在 Y 轴插值，混合出当前精确位置的平滑引导力。",
      "👉 右侧演示：观察红点移动时，如何受周围四个绿色固定向量的权重影响。"
    ],
    code: `// 双线性插值伪代码
// tx, ty 是当前坐标在四个网格中心间的小数偏移 (0~1)
const topLerp = lerp(vectorTL, vectorTR, tx);
const bottomLerp = lerp(vectorBL, vectorBR, tx);
const finalVector = lerp(topLerp, bottomLerp, ty);

function lerp(a, b, t) {
  return a + (b - a) * t;
}`,
    visualMode: "bilinear_demo"
  },
  {
    id: 9,
    title: "深入解析：分离避障机制",
    subtitle: "Deep Dive: Separation Steering",
    content: [
      "感知半径：每个单位只关心距离自己一定半径（Perception Radius）内的“邻居”，这极大减少了计算量。",
      "计算斥力：遍历感知到的邻居，计算从邻居指向自己的向量。",
      "距离反比衰减：距离越近，产生的排斥力越强（通常通过 1/d 实现）。",
      "👉 右侧演示：红圈为感知范围，观察邻居侵入时产生的红色排斥力。"
    ],
    code: `// 分离斥力核心逻辑
let separationForce = { x: 0, y: 0 };
let count = 0;

for (const neighbor of units) {
  const dist = distance(this, neighbor);
  
  if (dist > 0 && dist < PERCEPTION_RADIUS) {
    // 计算排斥方向
    let diff = sub(this.pos, neighbor.pos);
    // 距离越近，排斥力越大 (归一化后 / dist)
    diff = normalize(diff);
    diff.x /= dist; 
    diff.y /= dist;
    
    separationForce.x += diff.x;
    separationForce.y += diff.y;
    count++;
  }
}`,
    visualMode: "separation_demo"
  },
  {
    id: 10,
    title: "深入交互：单位间避障",
    subtitle: "Interactive Demo: Separation",
    content: [
      "演示场景：多个单位同时试图前往同一个中心目标点。",
      "参数调节：通过右侧的滑块可以实时调节“单位间的排斥力大小”。",
      "现象观察：斥力过小会导致单位重叠穿模；斥力适当则能形成均匀的包围圈；斥力过大甚至会导致单位发生剧烈弹射。"
    ],
    visualMode: "interactive_separation"
  },
  {
    id: 11,
    title: "深入交互：障碍物避障",
    subtitle: "Interactive Demo: Obstacle Avoidance",
    content: [
      "演示场景：寻路单位试图穿过中间的圆形障碍物，前往右侧的绿色目标点。",
      "参数调节：通过右侧的滑块可以实时调节“障碍物产生的排斥力大小”。",
      "现象观察：排斥力能在单位撞上物理障碍前（红色虚线圈为感知范围）提前赋予其法向推力。通过调节斥力，你可以清晰地观察到单位是如何改变航向绕行的。"
    ],
    visualMode: "interactive_avoidance"
  },
  {
    id: 12,
    title: "第三部分：力的应用与平滑避障",
    subtitle: "Step 3 & 4: Forces, Interpolation & Avoidance",
    content: [
      "力的读取：单位移动时，直接读取所在网格的向量，获得移动推力。",
      "双线性插值 (Bilinear Interpolation)：平滑网格边缘的受力，使移动更加自然。",
      "分离避障 (Separation)：结合 Steering Behavior。为节省算力，只处理与周围“邻居”单位的分离避障，无需全局计算。"
    ],
    visualMode: "flow"
  },
  {
    id: 13,
    title: "深入解析：修复角落卡死",
    subtitle: "Deep Dive: Diagonal Corner Cutting Trap",
    content: [
      "问题现象：如右侧图解，当地图出现对角线交叉的障碍物时，群体寻路时常会卡死在夹角处不断震颤。",
      "根本原因：寻路单元拥有物理碰撞体积，但在生成 8 方向向量场时，基础算法允许了不切实际的“对角线穿透”指引，导致力场与物理碰撞冲突。",
      "改进算法：在生成向量场搜寻最低成本网格时，增加“相邻墙壁”判定。如果水平或垂直方向存在障碍物，则物理体积必定受阻，应直接剔除该对角线的通行许可。",
      "👉 右侧演示：图解对角线防穿模拦截。此算法已应用至全局，后续寻路将不再出现卡死死角。"
    ],
    code: `// 防止对角线穿模核心逻辑 (Vector Field 生成阶段)
for (let dy = -1; dy <= 1; dy++) {
  for (let dx = -1; dx <= 1; dx++) {
    if (dx === 0 && dy === 0) continue;

    // --- 新增：禁止对角线穿墙检测 ---
    if (dx !== 0 && dy !== 0) {
      const nodeX = costField[getIndex(x + dx, y)];
      const nodeY = costField[getIndex(x, y + dy)];
      // 如果两侧任一是障碍物，物理上无法斜穿，跳过该方向
      if (nodeX === OBSTACLE_COST || nodeY === OBSTACLE_COST) {
        continue;
      }
    }

    // ... 记录最低 Cost 并计算向量 ...
  }
}`,
    visualMode: "corner_demo"
  },
  {
    id: 14,
    title: "深入解析：时空复杂度对比",
    subtitle: "Deep Dive: Time & Space Complexity",
    content: [
      "传统 A* 算法 (O(N))：计算时耗与“寻路单位数量 (N)”呈正相关。单位越多，CPU 需要进行的路径搜寻次数呈线性爆炸增长。",
      "向量场算法 (O(G))：计算时耗主要取决于“地图网格数量 (G)”。无论地图上有 10 个还是 10000 个单位，底层流场只需计算 1 次！",
      "空间换时间：向量场需要为全图每个网格额外开辟内存，以存储 Cost、距离场和方向向量。这是非常典型的“牺牲空间换取极致时间”策略。",
      "👉 右侧演示：动态性能耗时折线图（概念模型）。注意观察两者在不同单位数量下的效率交叉点。"
    ],
    visualMode: "complexity_demo"
  },
  {
    id: 15,
    title: "第四部分：最终成果与开源",
    subtitle: "Demo & Open Source",
    content: [
      "你可以看到海量单位如流水般绕开障碍物，顺滑地汇聚到目标点。",
      "在实际项目中，还可以加入动态障碍物更新、不同体型单位的处理等细节。",
      "致谢参考资料：B站 UP主 @Sli97"
    ],
    links: [
      { text: "DEMO 开源地址", url: "https://github.com/Kevin23-design/AI-Fundamentals-2026-Spring", icon: Github },
      { text: "参考视频：流场寻路算法如何实现", url: "https://www.bilibili.com/video/BV12bzZY2EfA", icon: Video },
      { text: "参考文章：Craig W. Reynolds (GDC 1999)", url: "https://www.red3d.com/cwr/steer/gdc99/", icon: Link },
      { text: "参考分享：GDC 2011 AI Navigation", url: "https://gdcvault.com/play/1014514/AI-Navigation-It-s-Not", icon: Video },
      { text: "参考源码：《游戏人工智能编程案例精粹》", url: "https://gitee.com/sli97/steering-book", icon: Github }
    ],
    visualMode: "flow_large"
  }
];

// --- 向量场算法核心逻辑 ---
class FlowField {
  constructor(cols, rows) {
    this.cols = cols;
    this.rows = rows;
    this.costField = new Array(cols * rows).fill(NORMAL_COST);
    this.integrationField = new Array(cols * rows).fill(65535);
    this.visitTimeField = new Array(cols * rows).fill(65535);
    this.vectorField = new Array(cols * rows).fill(null).map(() => ({ x: 0, y: 0 }));
    this.target = { x: cols - 2, y: Math.floor(rows / 2) };
    this.enableCornerFix = false;
    this.generateObstacles();
    this.calculate();
  }

  getIndex(x, y) {
    if (x < 0 || x >= this.cols || y < 0 || y >= this.rows) return -1;
    return y * this.cols + x;
  }

  generateObstacles() {
    for (let i = 0; i < 12; i++) {
      const w = Math.floor(Math.random() * 3) + 1;
      const h = Math.floor(Math.random() * 3) + 1;
      const startX = Math.floor(Math.random() * (this.cols - w - 4)) + 2;
      const startY = Math.floor(Math.random() * (this.rows - h));
      for (let x = startX; x < startX + w; x++) {
        for (let y = startY; y < startY + h; y++) {
          this.costField[this.getIndex(x, y)] = OBSTACLE_COST;
        }
      }
    }
  }

  setTarget(x, y) {
    if (this.costField[this.getIndex(x, y)] !== OBSTACLE_COST) {
      this.target = { x, y };
      this.calculate();
    }
  }

  calculate() {
    this.integrationField.fill(65535);
    this.visitTimeField.fill(65535);
    const targetIndex = this.getIndex(this.target.x, this.target.y);
    if (targetIndex === -1) return;

    this.integrationField[targetIndex] = 0;
    this.visitTimeField[targetIndex] = 0;
    let stepCounter = 1;
    const queue = [this.target];

    while (queue.length > 0) {
      const current = queue.shift();
      const currIdx = this.getIndex(current.x, current.y);
      const currCost = this.integrationField[currIdx];

      const neighbors = [
        { x: current.x, y: current.y - 1 }, { x: current.x, y: current.y + 1 },
        { x: current.x - 1, y: current.y }, { x: current.x + 1, y: current.y }
      ];

      for (const n of neighbors) {
        const nIdx = this.getIndex(n.x, n.y);
        if (nIdx === -1) continue;
        const moveCost = this.costField[nIdx];
        if (moveCost === OBSTACLE_COST) continue;

        const newCost = currCost + moveCost;
        if (newCost < this.integrationField[nIdx]) {
          this.integrationField[nIdx] = newCost;
          this.visitTimeField[nIdx] = stepCounter++;
          queue.push(n);
        }
      }
    }

    for (let y = 0; y < this.rows; y++) {
      for (let x = 0; x < this.cols; x++) {
        const idx = this.getIndex(x, y);
        if (this.costField[idx] === OBSTACLE_COST || this.integrationField[idx] === 65535) {
          this.vectorField[idx] = { x: 0, y: 0 };
          continue;
        }

        let minCost = this.integrationField[idx];
        let minX = 0, minY = 0;

        for (let dy = -1; dy <= 1; dy++) {
          for (let dx = -1; dx <= 1; dx++) {
            if (dx === 0 && dy === 0) continue;

            if (dx !== 0 && dy !== 0 && this.enableCornerFix) {
               const idxX = this.getIndex(x + dx, y);
               const idxY = this.getIndex(x, y + dy);
               if ((idxX !== -1 && this.costField[idxX] === OBSTACLE_COST) ||
                   (idxY !== -1 && this.costField[idxY] === OBSTACLE_COST)) {
                   continue;
               }
            }

            const nIdx = this.getIndex(x + dx, y + dy);
            if (nIdx !== -1 && this.costField[nIdx] !== OBSTACLE_COST) {
              if (this.integrationField[nIdx] < minCost) {
                minCost = this.integrationField[nIdx];
                minX = dx;
                minY = dy;
              }
            }
          }
        }

        const mag = Math.sqrt(minX * minX + minY * minY);
        if (mag > 0) {
          this.vectorField[idx] = { x: minX / mag, y: minY / mag };
        } else {
          this.vectorField[idx] = { x: 0, y: 0 };
        }
      }
    }
  }
}

class Particle {
  constructor(x, y) {
    this.pos = { x, y };
    this.vel = { x: 0, y: 0 };
    this.maxSpeed = 1.5 + Math.random() * 0.5;
    this.radius = 8;
  }

  update(flowField, particles) {
    const gridX = Math.floor(this.pos.x / GRID_SIZE);
    const gridY = Math.floor(this.pos.y / GRID_SIZE);
    const idx = flowField.getIndex(gridX, gridY);

    let desired = { x: 0, y: 0 };

    if (idx !== -1 && flowField.costField[idx] !== OBSTACLE_COST) {
      desired = flowField.vectorField[idx];
    }

    const steerX = (desired.x * this.maxSpeed) - this.vel.x;
    const steerY = (desired.y * this.maxSpeed) - this.vel.y;

    let sepX = 0, sepY = 0, count = 0;
    const perceptionRadius = 12;
    for (const other of particles) {
      if (other !== this) {
        const dx = this.pos.x - other.pos.x;
        const dy = this.pos.y - other.pos.y;
        const d = Math.sqrt(dx * dx + dy * dy);
        if (d > 0 && d < perceptionRadius) {
          sepX += dx / d;
          sepY += dy / d;
          count++;
        }
      }
    }
    if (count > 0) {
      sepX /= count; sepY /= count;
      const sepMag = Math.sqrt(sepX * sepX + sepY * sepY);
      if (sepMag > 0) {
        sepX = (sepX / sepMag) * this.maxSpeed;
        sepY = (sepY / sepMag) * this.maxSpeed;
      }
    }

    this.vel.x += steerX * 0.1 + sepX * 0.15;
    this.vel.y += steerY * 0.1 + sepY * 0.15;

    const speed = Math.sqrt(this.vel.x * this.vel.x + this.vel.y * this.vel.y);
    if (speed > this.maxSpeed) {
      this.vel.x = (this.vel.x / speed) * this.maxSpeed;
      this.vel.y = (this.vel.y / speed) * this.maxSpeed;
    }

    let nextX = this.pos.x + this.vel.x;
    let nextY = this.pos.y + this.vel.y;
    
    let gridXNext = Math.floor(nextX / GRID_SIZE);
    let gridYCurrent = Math.floor(this.pos.y / GRID_SIZE);
    let idxX = flowField.getIndex(gridXNext, gridYCurrent);
    if (idxX !== -1 && flowField.costField[idxX] === OBSTACLE_COST) {
      this.vel.x *= -0.5;
      nextX = this.pos.x;
    }

    let gridXCurrent = Math.floor(this.pos.x / GRID_SIZE);
    let gridYNext = Math.floor(nextY / GRID_SIZE);
    let idxY = flowField.getIndex(gridXCurrent, gridYNext);
    if (idxY !== -1 && flowField.costField[idxY] === OBSTACLE_COST) {
      this.vel.y *= -0.5;
      nextY = this.pos.y;
    }

    this.pos.x = nextX;
    this.pos.y = nextY;

    if (this.pos.x < 0) this.pos.x = 0;
    if (this.pos.x >= CANVAS_WIDTH) this.pos.x = CANVAS_WIDTH - 1;
    if (this.pos.y < 0) this.pos.y = 0;
    if (this.pos.y >= CANVAS_HEIGHT) this.pos.y = CANVAS_HEIGHT - 1;
  }
}

// --- React 组件 ---
export default function App() {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [expandedCode, setExpandedCode] = useState(null);
  
  // 新增：交互场景控制参数
  const [sepForce, setSepForce] = useState(40);
  const [avoForce, setAvoForce] = useState(60);
  
  // 新增：AI 助教聊天状态
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const chatEndRef = useRef(null);

  const canvasRef = useRef(null);
  const bfsProgressRef = useRef(0);
  
  const flowField = useMemo(() => new FlowField(COLS, ROWS), []);

  const simState = useRef({
      sepUnits: [],
      avoUnits: []
  });

  const getRandomFreePos = (field) => {
    let x, y, gridX, gridY, idx;
    let attempts = 0;
    do {
      x = Math.random() * (CANVAS_WIDTH / 4);
      y = Math.random() * CANVAS_HEIGHT;
      gridX = Math.floor(x / GRID_SIZE);
      gridY = Math.floor(y / GRID_SIZE);
      idx = field.getIndex(gridX, gridY);
      attempts++;
    } while (idx !== -1 && field.costField[idx] === OBSTACLE_COST && attempts < 100);
    return { x, y };
  };

  const particles = useMemo(() => {
    const pts = [];
    for (let i = 0; i < NUM_PARTICLES; i++) {
      const pos = getRandomFreePos(flowField);
      pts.push(new Particle(pos.x, pos.y));
    }
    return pts;
  }, [flowField]);

  const slide = SLIDES[currentSlide];

  // 翻页时状态重置与场景初始化
  useEffect(() => {
    setIsPlaying(false);
    bfsProgressRef.current = 0;

    const shouldFix = currentSlide >= 12;
    if (flowField.enableCornerFix !== shouldFix) {
      flowField.enableCornerFix = shouldFix;
      flowField.calculate();
    }

    particles.forEach(p => {
      const pos = getRandomFreePos(flowField);
      p.pos.x = pos.x;
      p.pos.y = pos.y;
      p.vel = { x: 0, y: 0 };
    });

    if (SLIDES[currentSlide].visualMode === 'interactive_separation') {
        const units = [];
        for(let i=0; i<15; i++) {
            units.push({
                x: CANVAS_WIDTH/2 + (Math.random()*200 - 100),
                y: CANVAS_HEIGHT/2 + (Math.random()*200 - 100),
                vx: 0, vy: 0
            });
        }
        simState.current.sepUnits = units;
    } else if (SLIDES[currentSlide].visualMode === 'interactive_avoidance') {
        simState.current.avoUnits = [
            {x: 60, y: CANVAS_HEIGHT/2, vx: 2, vy: 0},
            {x: 40, y: CANVAS_HEIGHT/2 - 25, vx: 2, vy: 0},
            {x: 40, y: CANVAS_HEIGHT/2 + 25, vx: 2, vy: 0},
            {x: 20, y: CANVAS_HEIGHT/2 - 10, vx: 2, vy: 0},
            {x: 20, y: CANVAS_HEIGHT/2 + 10, vx: 2, vy: 0}
        ];
    }
  }, [currentSlide, particles, flowField]);

  const handleNext = () => setCurrentSlide(p => Math.min(SLIDES.length - 1, p + 1));
  const handlePrev = () => setCurrentSlide(p => Math.max(0, p - 1));

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'ArrowRight' || e.key === 'Space') handleNext();
      if (e.key === 'ArrowLeft') handlePrev();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // AI 助教：自动滚动到底部
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages, isTyping]);

  const handleCanvasClick = (e) => {
    if (!canvasRef.current) return;
    const rect = canvasRef.current.getBoundingClientRect();
    const scaleX = CANVAS_WIDTH / rect.width;
    const scaleY = CANVAS_HEIGHT / rect.height;
    const x = Math.floor(((e.clientX - rect.left) * scaleX) / GRID_SIZE);
    const y = Math.floor(((e.clientY - rect.top) * scaleY) / GRID_SIZE);
    flowField.setTarget(x, y);
    bfsProgressRef.current = 0;
  };

  // 调用 Gemini API
  const handleSendMessage = async () => {
    if (!chatInput.trim()) return;
    const userMsg = { role: 'user', text: chatInput };
    setChatMessages(prev => [...prev, userMsg]);
    setChatInput('');
    setIsTyping(true);

    const apiKey = "";
    const currentSlideContext = SLIDES[currentSlide];
    const sysPrompt = `你是一个名为“AI演示助教”的辅助系统，协助演讲者进行关于向量场群体寻路算法(Vector Field Pathfinding)的演讲。
当前观众和演讲者正在观看的幻灯片内容如下：
标题: ${currentSlideContext.title}
副标题: ${currentSlideContext.subtitle}
内容要点: ${currentSlideContext.content.join(' | ')}
代码上下文: ${currentSlideContext.code ? currentSlideContext.code : '无代码'}

请根据上述上下文以及寻路算法的专业知识，简明扼要地回答观众提出的疑问。回答语气要友好、专业，必须使用中文回复。`;

    const payload = {
      contents: [{ parts: [{ text: userMsg.text }] }],
      systemInstruction: { parts: [{ text: sysPrompt }] }
    };

    let delay = 1000;
    let responseText = "抱歉，由于网络或接口问题，AI助手暂时无法响应，请稍后再试。";
    
    for (let i = 0; i < 5; i++) {
      try {
        const res = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key=${apiKey}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error('API Error');
        const data = await res.json();
        responseText = data.candidates?.[0]?.content?.parts?.[0]?.text || "抱歉，我未能生成有效回答。";
        break;
      } catch (err) {
        if (i < 4) {
          await new Promise(r => setTimeout(r, delay));
          delay *= 2;
        }
      }
    }

    setChatMessages(prev => [...prev, { role: 'ai', text: responseText }]);
    setIsTyping(false);
  };

  // Canvas 渲染循环
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animationId;

    const render = () => {
      ctx.clearRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
      
      const { visualMode } = SLIDES[currentSlide];
      
      let currentDrawLimit = Infinity;
      if (visualMode === 'bfs_step') {
        currentDrawLimit = bfsProgressRef.current;
        bfsProgressRef.current += 3;
      }

      // === 渲染分支控制 ===
      if (visualMode === 'title') {
         ctx.fillStyle = '#1e293b';
         ctx.fillRect(0,0, CANVAS_WIDTH, CANVAS_HEIGHT);
      } else if (visualMode === 'agenda') {
        ctx.fillStyle = '#0f172a';
        ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

        const time = Date.now() * 0.001;
        const nodes = [
          { label: "1. 痛点展示", x: CANVAS_WIDTH * 0.2, y: CANVAS_HEIGHT * 0.25 },
          { label: "2. 向量场方案", x: CANVAS_WIDTH * 0.8, y: CANVAS_HEIGHT * 0.25 },
          { label: "3. 核心算法实现", x: CANVAS_WIDTH * 0.8, y: CANVAS_HEIGHT * 0.5 },
          { label: "4. 深入原理解析", x: CANVAS_WIDTH * 0.2, y: CANVAS_HEIGHT * 0.5 },
          { label: "5. 复杂度分析", x: CANVAS_WIDTH * 0.2, y: CANVAS_HEIGHT * 0.75 },
          { label: "6. 成果与开源", x: CANVAS_WIDTH * 0.8, y: CANVAS_HEIGHT * 0.75 }
        ];

        ctx.strokeStyle = '#334155';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(nodes[0].x, nodes[0].y);
        for(let i = 1; i < nodes.length; i++) ctx.lineTo(nodes[i].x, nodes[i].y);
        ctx.stroke();

        const pathLength = nodes.length - 1;
        const currentSegment = Math.floor(time) % pathLength;
        const segProgress = time % 1;
        const easeInOut = (t) => t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
        const smoothProgress = easeInOut(segProgress);

        const p1 = nodes[currentSegment];
        const p2 = nodes[currentSegment + 1];
        const pulseX = p1.x + (p2.x - p1.x) * smoothProgress;
        const pulseY = p1.y + (p2.y - p1.y) * smoothProgress;

        ctx.fillStyle = '#10b981';
        ctx.shadowColor = '#10b981';
        ctx.shadowBlur = 20;
        ctx.beginPath();
        ctx.arc(pulseX, pulseY, 8, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0;

        nodes.forEach((n, i) => {
          ctx.fillStyle = '#1e293b';
          ctx.strokeStyle = '#10b981';
          ctx.lineWidth = 2;
          ctx.beginPath(); ctx.arc(n.x, n.y, 14, 0, Math.PI * 2); ctx.fill(); ctx.stroke();

          ctx.fillStyle = '#cbd5e1';
          ctx.font = 'bold 16px Arial';
          ctx.textAlign = (i === 0 || i === 3 || i === 4) ? 'left' : 'right';
          const xOffset = (i === 0 || i === 3 || i === 4) ? 25 : -25;
          ctx.fillText(n.label, n.x + xOffset, n.y + 5);
        });

      } else if (visualMode === 'bilinear_demo') {
        const time = Date.now() * 0.0015;
        const cx = CANVAS_WIDTH / 2;
        const cy = CANVAS_HEIGHT / 2;
        const s = 100;
        
        ctx.fillStyle = '#0f172a';
        ctx.fillRect(0,0, CANVAS_WIDTH, CANVAS_HEIGHT);

        ctx.strokeStyle = '#334155';
        ctx.setLineDash([5, 5]);
        ctx.strokeRect(cx - s, cy - s, s*2, s*2);
        ctx.setLineDash([]);
        ctx.beginPath(); ctx.moveTo(cx, cy-s); ctx.lineTo(cx, cy+s); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(cx-s, cy); ctx.lineTo(cx+s, cy); ctx.stroke();

        const corners = [
          { x: cx - s/2, y: cy - s/2, v: { x: 1, y: 0.2 }, color: '#10b981' },
          { x: cx + s/2, y: cy - s/2, v: { x: 0, y: 1 }, color: '#10b981' },
          { x: cx - s/2, y: cy + s/2, v: { x: 0.5, y: -1 }, color: '#10b981' },
          { x: cx + s/2, y: cy + s/2, v: { x: -1, y: -0.5 }, color: '#10b981' }
        ];

        const drawArrow = (fromX, fromY, vecX, vecY, color, length, width = 2) => {
           ctx.strokeStyle = color; ctx.fillStyle = color; ctx.lineWidth = width;
           ctx.beginPath(); ctx.moveTo(fromX, fromY); ctx.lineTo(fromX + vecX*length, fromY + vecY*length); ctx.stroke();
           ctx.beginPath(); ctx.arc(fromX + vecX*length, fromY + vecY*length, 3, 0, Math.PI*2); ctx.fill();
        };

        corners.forEach(c => {
          ctx.fillStyle = '#334155'; ctx.beginPath(); ctx.arc(c.x, c.y, 6, 0, Math.PI*2); ctx.fill();
          drawArrow(c.x, c.y, c.v.x, c.v.y, c.color, 40);
        });

        const px = cx + Math.sin(time) * (s/2 - 10);
        const py = cy + Math.cos(time * 0.8) * (s/2 - 10);
        
        const tx = (px - corners[0].x) / s;
        const ty = (py - corners[0].y) / s;

        ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)'; ctx.lineWidth = 1;
        corners.forEach(c => { ctx.beginPath(); ctx.moveTo(px, py); ctx.lineTo(c.x, c.y); ctx.stroke(); });

        const topX = corners[0].v.x + (corners[1].v.x - corners[0].v.x) * tx;
        const topY = corners[0].v.y + (corners[1].v.y - corners[0].v.y) * tx;
        const botX = corners[2].v.x + (corners[3].v.x - corners[2].v.x) * tx;
        const botY = corners[2].v.y + (corners[3].v.y - corners[2].v.y) * tx;
        const finalX = topX + (botX - topX) * ty;
        const finalY = topY + (botY - topY) * ty;

        drawArrow(px, py, finalX, finalY, '#f59e0b', 60, 3);
        ctx.fillStyle = '#ef4444'; ctx.beginPath(); ctx.arc(px, py, 8, 0, Math.PI*2); ctx.fill();
        
        ctx.fillStyle = '#cbd5e1'; ctx.font = '12px Arial';
        ctx.fillText(`Lerp X: ${tx.toFixed(2)}`, px + 15, py - 10);
        ctx.fillText(`Lerp Y: ${ty.toFixed(2)}`, px + 15, py + 5);

      } else if (visualMode === 'separation_demo') {
        const time = Date.now() * 0.002;
        const cx = CANVAS_WIDTH / 2;
        const cy = CANVAS_HEIGHT / 2;
        const radius = 120;
        
        ctx.fillStyle = '#0f172a';
        ctx.fillRect(0,0, CANVAS_WIDTH, CANVAS_HEIGHT);

        ctx.strokeStyle = 'rgba(16, 185, 129, 0.3)'; ctx.lineWidth = 2;
        ctx.beginPath(); ctx.arc(cx, cy, radius, 0, Math.PI*2); ctx.stroke();
        ctx.fillStyle = 'rgba(16, 185, 129, 0.05)'; ctx.fill();
        ctx.fillStyle = '#3b82f6'; ctx.beginPath(); ctx.arc(cx, cy, 10, 0, Math.PI*2); ctx.fill();
        
        const neighbors = [
          { x: cx + Math.cos(time) * 80, y: cy + Math.sin(time) * 80 },
          { x: cx + Math.cos(-time*0.5 + 2) * 60, y: cy + Math.sin(-time*0.5 + 2) * 60 },
          { x: cx + Math.cos(time*0.3) * 160, y: cy + Math.sin(time*0.3) * 160 }
        ];

        let totalForceX = 0, totalForceY = 0;

        neighbors.forEach(n => {
          ctx.fillStyle = '#94a3b8'; ctx.beginPath(); ctx.arc(n.x, n.y, 10, 0, Math.PI*2); ctx.fill();
          const dx = cx - n.x;
          const dy = cy - n.y;
          const dist = Math.sqrt(dx*dx + dy*dy);
          
          if (dist < radius) {
            ctx.strokeStyle = '#ef4444'; ctx.setLineDash([4, 4]); ctx.lineWidth = 1;
            ctx.beginPath(); ctx.moveTo(n.x, n.y); ctx.lineTo(cx, cy); ctx.stroke(); ctx.setLineDash([]);
            
            const forceMag = (radius - dist) / radius * 50; 
            const forceX = (dx / dist) * forceMag;
            const forceY = (dy / dist) * forceMag;
            
            ctx.strokeStyle = 'rgba(239, 68, 68, 0.5)'; ctx.lineWidth = 2;
            ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(cx + forceX, cy + forceY); ctx.stroke();
            
            totalForceX += forceX; totalForceY += forceY;
          } else {
             ctx.strokeStyle = '#334155'; ctx.setLineDash([4, 4]);
             ctx.beginPath(); ctx.moveTo(n.x, n.y); ctx.lineTo(cx, cy); ctx.stroke(); ctx.setLineDash([]);
          }
        });

        if (totalForceX !== 0 || totalForceY !== 0) {
           ctx.strokeStyle = '#ef4444'; ctx.fillStyle = '#ef4444'; ctx.lineWidth = 3;
           ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(cx + totalForceX, cy + totalForceY); ctx.stroke();
           ctx.beginPath(); ctx.arc(cx + totalForceX, cy + totalForceY, 4, 0, Math.PI*2); ctx.fill();
           ctx.font = '14px Arial'; ctx.fillText('排斥合力', cx + totalForceX + 10, cy + totalForceY);
        }

      } else if (visualMode === 'interactive_separation') {
        // === 新增：可滑块调节的交互分离场景 ===
        ctx.fillStyle = '#0f172a';
        ctx.fillRect(0,0, CANVAS_WIDTH, CANVAS_HEIGHT);

        const cx = CANVAS_WIDTH / 2;
        const cy = CANVAS_HEIGHT / 2;

        ctx.fillStyle = 'rgba(16, 185, 129, 0.2)';
        ctx.beginPath(); ctx.arc(cx, cy, 20, 0, Math.PI*2); ctx.fill();
        ctx.fillStyle = '#10b981';
        ctx.beginPath(); ctx.arc(cx, cy, 6, 0, Math.PI*2); ctx.fill();

        simState.current.sepUnits.forEach(u => {
           const dx = cx - u.x; const dy = cy - u.y;
           const d = Math.sqrt(dx*dx + dy*dy) || 1;
           let steerX = (dx/d) * 2.0; let steerY = (dy/d) * 2.0;

           let localSepX = 0, localSepY = 0;
           simState.current.sepUnits.forEach(other => {
               if (u !== other) {
                   const odx = u.x - other.x; const ody = u.y - other.y;
                   const od = Math.sqrt(odx*odx + ody*ody);
                   if (od > 0 && od < 50) { 
                       const force = (sepForce / 20) * ((50 - od) / 50);
                       localSepX += (odx/od) * force;
                       localSepY += (ody/od) * force;
                       
                       if (od < 25 && sepForce > 0) {
                           ctx.strokeStyle = `rgba(239, 68, 68, ${Math.min(1, force * 0.3)})`;
                           ctx.lineWidth = 1;
                           ctx.beginPath(); ctx.moveTo(u.x, u.y); ctx.lineTo(other.x, other.y); ctx.stroke();
                       }
                   }
               }
           });

           u.vx = u.vx * 0.85 + steerX * 0.15 + localSepX * 0.2;
           u.vy = u.vy * 0.85 + steerY * 0.15 + localSepY * 0.2;

           const speed = Math.sqrt(u.vx*u.vx + u.vy*u.vy);
           if (speed > 3.5) { u.vx = (u.vx/speed)*3.5; u.vy = (u.vy/speed)*3.5; }

           u.x += u.vx; u.y += u.vy;

           ctx.fillStyle = '#3b82f6';
           ctx.beginPath(); ctx.arc(u.x, u.y, 8, 0, Math.PI*2); ctx.fill();
        });

      } else if (visualMode === 'interactive_avoidance') {
        // === 新增：可滑块调节的交互避障场景 ===
        ctx.fillStyle = '#0f172a';
        ctx.fillRect(0,0, CANVAS_WIDTH, CANVAS_HEIGHT);

        const cx = CANVAS_WIDTH / 2;
        const cy = CANVAS_HEIGHT / 2;
        const obsR = 45;
        const targetX = CANVAS_WIDTH - 80;
        const targetY = cy;

        ctx.fillStyle = 'rgba(16, 185, 129, 0.2)';
        ctx.beginPath(); ctx.arc(targetX, targetY, 20, 0, Math.PI*2); ctx.fill();
        ctx.fillStyle = '#10b981';
        ctx.beginPath(); ctx.arc(targetX, targetY, 6, 0, Math.PI*2); ctx.fill();

        ctx.fillStyle = '#334155';
        ctx.beginPath(); ctx.arc(cx, cy, obsR, 0, Math.PI*2); ctx.fill();
        ctx.strokeStyle = '#1e293b'; ctx.lineWidth = 4;
        ctx.beginPath(); ctx.arc(cx, cy, obsR, 0, Math.PI*2); ctx.stroke();

        const avoidRadius = obsR + 60;
        ctx.strokeStyle = 'rgba(239, 68, 68, 0.4)';
        ctx.setLineDash([5, 5]); ctx.lineWidth = 1;
        ctx.beginPath(); ctx.arc(cx, cy, avoidRadius, 0, Math.PI*2); ctx.stroke();
        ctx.setLineDash([]);

        simState.current.avoUnits.forEach(u => {
           if (Math.sqrt((u.x-targetX)**2 + (u.y-targetY)**2) < 25 || u.x > CANVAS_WIDTH - 20) {
               u.x = 60; u.y = cy + (Math.random()*60-30); u.vx=2; u.vy=0;
           }

           const dx = targetX - u.x; const dy = targetY - u.y;
           const d = Math.sqrt(dx*dx + dy*dy) || 1;
           let steerX = (dx/d) * 2.5; let steerY = (dy/d) * 2.5;

           let localAvoX = 0, localAvoY = 0;
           const odx = u.x - cx; const ody = u.y - cy;
           const od = Math.sqrt(odx*odx + ody*ody);

           if (od < avoidRadius) {
               const force = (avoForce / 15) * ((avoidRadius - od) / avoidRadius);
               localAvoX = (odx/od) * force;
               localAvoY = (ody/od) * force;

               ctx.strokeStyle = 'rgba(245, 158, 11, 0.8)';
               ctx.lineWidth = 2;
               ctx.beginPath(); ctx.moveTo(u.x, u.y); ctx.lineTo(u.x + localAvoX*10, u.y + localAvoY*10); ctx.stroke();
           }

           u.vx = u.vx * 0.95 + steerX * 0.05 + localAvoX * 0.1;
           u.vy = u.vy * 0.95 + steerY * 0.05 + localAvoY * 0.1;

           const speed = Math.sqrt(u.vx*u.vx + u.vy*u.vy);
           if (speed > 3) { u.vx = (u.vx/speed)*3; u.vy = (u.vy/speed)*3; }

           u.x += u.vx; u.y += u.vy;

           ctx.fillStyle = '#3b82f6';
           ctx.beginPath(); ctx.arc(u.x, u.y, 8, 0, Math.PI*2); ctx.fill();
        });

      } else if (visualMode === 'corner_demo') {
        const cx = CANVAS_WIDTH / 2 - 40;
        const cy = CANVAS_HEIGHT / 2 - 40;
        const s = 80;

        ctx.fillStyle = '#0f172a';
        ctx.fillRect(0,0, CANVAS_WIDTH, CANVAS_HEIGHT);

        const drawCell = (x, y, isObstacle, label) => {
            ctx.fillStyle = isObstacle ? '#334155' : '#0f172a';
            ctx.fillRect(x, y, s, s);
            ctx.strokeStyle = '#1e293b';
            ctx.strokeRect(x, y, s, s);
            if (label) {
                ctx.fillStyle = isObstacle ? '#cbd5e1' : '#10b981';
                ctx.font = '14px Arial';
                ctx.textAlign = 'center';
                ctx.fillText(label, x + s/2, y + s/2 + 5);
            }
        };

        drawCell(cx, cy + s, false, "当前网格");
        drawCell(cx, cy, true, "障碍物");
        drawCell(cx + s, cy + s, true, "障碍物");
        drawCell(cx + s, cy, false, "低Cost目标");

        ctx.strokeStyle = 'rgba(239, 68, 68, 0.6)';
        ctx.setLineDash([5, 5]);
        ctx.lineWidth = 4;
        ctx.beginPath();
        ctx.moveTo(cx + s/2, cy + s + s/2);
        ctx.lineTo(cx + s + s/2, cy + s/2);
        ctx.stroke();
        ctx.setLineDash([]);

        const midX = cx + s;
        const midY = cy + s;
        ctx.strokeStyle = '#ef4444';
        ctx.lineWidth = 4;
        ctx.beginPath();
        ctx.moveTo(midX - 15, midY - 15);
        ctx.lineTo(midX + 15, midY + 15);
        ctx.moveTo(midX + 15, midY - 15);
        ctx.lineTo(midX - 15, midY + 15);
        ctx.stroke();

        ctx.fillStyle = '#ef4444';
        ctx.font = 'bold 16px Arial';
        ctx.textAlign = 'center';
        ctx.fillText("物理体积无法穿透！", cx + s, cy + s*2 + 30);
        
        ctx.fillStyle = '#94a3b8';
        ctx.font = '14px Arial';
        ctx.fillText("寻路算法已强制剔除该对角线方向向量的生成", cx + s, cy + s*2 + 55);

      } else if (visualMode === 'complexity_demo') {
        ctx.fillStyle = '#0f172a';
        ctx.fillRect(0,0, CANVAS_WIDTH, CANVAS_HEIGHT);

        const padding = 60;
        const chartW = CANVAS_WIDTH - padding * 2;
        const chartH = CANVAS_HEIGHT - padding * 2;
        const startX = padding;
        const startY = CANVAS_HEIGHT - padding;

        ctx.strokeStyle = '#334155';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(startX, padding);
        ctx.lineTo(startX, startY);
        ctx.lineTo(startX + chartW, startY);
        ctx.stroke();

        ctx.fillStyle = '#94a3b8';
        ctx.font = '14px Arial';
        ctx.textAlign = 'center';
        ctx.fillText("同屏寻路单位数量 (N)", CANVAS_WIDTH / 2, startY + 40);
        ctx.save();
        ctx.translate(startX - 40, CANVAS_HEIGHT / 2);
        ctx.rotate(-Math.PI / 2);
        ctx.fillText("CPU 寻路计算耗时", 0, 0);
        ctx.restore();

        const t = (Date.now() % 4000) / 3000;
        const progress = Math.min(1, t);

        const vfY = startY - chartH * 0.25;
        const aStarEndY = padding + 20;

        ctx.strokeStyle = '#10b981';
        ctx.lineWidth = 4;
        ctx.beginPath();
        ctx.moveTo(startX, vfY);
        ctx.lineTo(startX + chartW * progress, vfY);
        ctx.stroke();

        ctx.strokeStyle = '#ef4444';
        ctx.lineWidth = 4;
        ctx.beginPath();
        ctx.moveTo(startX, startY - 5);
        const currentAStarY = (startY - 5) + (aStarEndY - (startY - 5)) * progress;
        ctx.lineTo(startX + chartW * progress, currentAStarY);
        ctx.stroke();

        const intersectProgress = 0.23;
        const intersectX = startX + chartW * intersectProgress;
        
        if (progress > intersectProgress) {
            ctx.fillStyle = '#f59e0b';
            ctx.beginPath();
            ctx.arc(intersectX, vfY, 6, 0, Math.PI*2);
            ctx.fill();
            
            ctx.fillStyle = '#fcd34d';
            ctx.textAlign = 'left';
            ctx.font = '12px Arial';
            ctx.fillText("效率交叉点", intersectX + 15, vfY - 12);
            ctx.fillStyle = '#94a3b8';
            ctx.fillText("<- A* 更优", intersectX - 70, vfY - 12);
            ctx.fillText("向量场统治区 ->", intersectX + 15, vfY + 18);
        }

        ctx.fillStyle = '#10b981';
        ctx.fillRect(startX + 20, padding, 15, 15);
        ctx.fillStyle = '#cbd5e1';
        ctx.textAlign = 'left';
        ctx.fillText("向量场算法 (O(1) 随单位数)", startX + 45, padding + 12);

        ctx.fillStyle = '#ef4444';
        ctx.fillRect(startX + 20, padding + 25, 15, 15);
        ctx.fillStyle = '#cbd5e1';
        ctx.fillText("传统 A* 算法 (O(N))", startX + 45, padding + 37);

      } else {
        // === 常规地图与流场渲染 ===
        for (let y = 0; y < ROWS; y++) {
          for (let x = 0; x < COLS; x++) {
            const idx = flowField.getIndex(x, y);
            const cost = flowField.costField[idx];
            const px = x * GRID_SIZE;
            const py = y * GRID_SIZE;

            if (cost === OBSTACLE_COST) {
              ctx.fillStyle = '#334155';
              ctx.fillRect(px, py, GRID_SIZE, GRID_SIZE);
            } else if (visualMode === 'heatmap' || visualMode === 'vector' || visualMode === 'bfs_step') {
              const val = flowField.integrationField[idx];
              const visitTime = flowField.visitTimeField[idx];
              
              if (val < 65535 && visitTime <= currentDrawLimit) {
                const intensity = Math.min(1, val / 40);
                const r = Math.floor(255 * (1 - intensity));
                const b = Math.floor(255 * intensity);
                ctx.fillStyle = `rgba(${r}, 50, ${b}, 0.6)`;
                ctx.fillRect(px, py, GRID_SIZE, GRID_SIZE);
                
                if (visualMode === 'heatmap' || visualMode === 'bfs_step') {
                  ctx.fillStyle = 'rgba(255,255,255,0.7)';
                  ctx.font = '10px Arial';
                  ctx.textAlign = 'center';
                  ctx.fillText(val.toString(), px + GRID_SIZE/2, py + GRID_SIZE/2 + 4);
                }
              }
            } else {
              ctx.fillStyle = '#0f172a';
              ctx.fillRect(px, py, GRID_SIZE, GRID_SIZE);
              ctx.strokeStyle = '#1e293b';
              ctx.strokeRect(px, py, GRID_SIZE, GRID_SIZE);
            }
          }
        }

        if (visualMode === 'vector' || visualMode === 'problem') {
          ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
          ctx.lineWidth = 1;
          for (let y = 0; y < ROWS; y++) {
            for (let x = 0; x < COLS; x++) {
              const idx = flowField.getIndex(x, y);
              if (flowField.costField[idx] === OBSTACLE_COST) continue;
              const vec = flowField.vectorField[idx];
              if (vec.x === 0 && vec.y === 0) continue;

              const cx = x * GRID_SIZE + GRID_SIZE / 2;
              const cy = y * GRID_SIZE + GRID_SIZE / 2;
              ctx.beginPath();
              ctx.moveTo(cx, cy);
              ctx.lineTo(cx + vec.x * 10, cy + vec.y * 10);
              ctx.stroke();
              
              ctx.fillStyle = 'rgba(255, 255, 255, 0.4)';
              ctx.beginPath();
              ctx.arc(cx + vec.x * 10, cy + vec.y * 10, 2, 0, Math.PI * 2);
              ctx.fill();
            }
          }
        }

        const targetPx = flowField.target.x * GRID_SIZE + GRID_SIZE / 2;
        const targetPy = flowField.target.y * GRID_SIZE + GRID_SIZE / 2;
        ctx.fillStyle = '#ef4444';
        ctx.beginPath();
        ctx.arc(targetPx, targetPy, 8, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = '#fca5a5';
        ctx.lineWidth = 2;
        ctx.stroke();

        if (visualMode === 'flow' || visualMode === 'flow_large' || visualMode === 'problem') {
          particles.forEach(p => {
            if (isPlaying) p.update(flowField, particles);
            ctx.fillStyle = '#3b82f6';
            ctx.beginPath();
            ctx.arc(p.pos.x, p.pos.y, p.radius, 0, Math.PI * 2);
            ctx.fill();
          });
        }
      }

      animationId = requestAnimationFrame(render);
    };

    render();
    return () => cancelAnimationFrame(animationId);
  }, [currentSlide, flowField, particles, isPlaying, sepForce, avoForce]);

  return (
    <div className="flex flex-col h-screen bg-slate-900 text-slate-100 font-sans overflow-hidden">
      
      <div className="h-1 w-full bg-slate-800">
        <div 
          className="h-full bg-emerald-500 transition-all duration-300"
          style={{ width: `${((currentSlide) / (SLIDES.length - 1)) * 100}%` }}
        />
      </div>

      <div className="flex-1 flex overflow-hidden">
        <div className={`relative p-10 flex flex-col transition-all duration-500 overflow-y-auto ${slide.visualMode === 'title' ? 'w-full items-center justify-center text-center' : 'w-1/3 border-r border-slate-700'}`}>
          
          <h2 className="text-emerald-400 font-semibold tracking-wider uppercase text-sm mb-2">
            {slide.subtitle}
          </h2>
          <h1 className="text-4xl font-bold mb-8 leading-tight shrink-0">
            {slide.title}
          </h1>
          <ul className="space-y-4 text-lg text-slate-300 shrink-0">
            {slide.content.map((text, i) => (
              <li key={i} className="flex items-start">
                {slide.visualMode !== 'title' && <span className="text-emerald-500 mr-3 mt-1">✦</span>}
                <span className="leading-relaxed">{text}</span>
              </li>
            ))}
          </ul>

          {slide.code && (
            <div className="mt-8 bg-slate-950 p-5 rounded-xl border border-slate-700 shadow-inner w-full overflow-x-auto relative group shrink-0">
              <button
                onClick={() => setExpandedCode(slide.code)}
                className="absolute top-3 right-3 p-1.5 bg-slate-800/80 text-slate-400 hover:text-white hover:bg-slate-700 rounded-md opacity-0 group-hover:opacity-100 transition-all z-10"
                title="全屏放大代码"
              >
                <Maximize className="w-4 h-4" />
              </button>
              <pre className="text-sm font-mono text-emerald-300 leading-relaxed whitespace-pre">
                <code>{slide.code}</code>
              </pre>
            </div>
          )}
          
          {slide.links && (
            <div className="mt-10 space-y-3">
              {slide.links.map((link, i) => {
                const Icon = link.icon;
                return (
                  <a key={i} href={link.url} target="_blank" rel="noreferrer" 
                     className="flex items-center p-3 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors border border-slate-600 w-fit">
                    <Icon className="w-5 h-5 mr-3 text-emerald-400" />
                    <span className="text-sm font-medium">{link.text}</span>
                  </a>
                );
              })}
            </div>
          )}
        </div>

        {slide.visualMode !== 'title' && (
          <div className="w-2/3 p-8 flex flex-col items-center justify-center bg-slate-950 relative">
            <div className="absolute top-4 right-6 flex items-center text-slate-400 text-sm bg-slate-900 px-3 py-1 rounded-full border border-slate-700">
              <span className="mr-2 w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              {slide.visualMode === 'agenda' && "流程概览与结构演示"}
              {!['bilinear_demo', 'separation_demo', 'corner_demo', 'complexity_demo', 'agenda', 'interactive_separation', 'interactive_avoidance'].includes(slide.visualMode) && "Live Canvas Demo (点击地图任意处可改变终点)"}
              {['bilinear_demo', 'separation_demo', 'corner_demo', 'complexity_demo', 'interactive_separation', 'interactive_avoidance'].includes(slide.visualMode) && "Live Canvas Demo (核心原理图解演示)"}
            </div>

            {/* 分离避障交互滑块 */}
            {slide.visualMode === 'interactive_separation' && (
              <div className="absolute bottom-6 right-6 z-10 bg-slate-900/90 p-5 rounded-xl border border-slate-700 shadow-2xl backdrop-blur-sm w-72">
                  <div className="flex justify-between items-center mb-3">
                      <span className="text-sm text-emerald-400 font-bold">单位间排斥力 (Separation)</span>
                      <span className="text-sm text-slate-300 font-mono bg-slate-800 px-2 rounded">{sepForce}</span>
                  </div>
                  <input
                      type="range" min="0" max="150" value={sepForce}
                      onChange={(e) => setSepForce(Number(e.target.value))}
                      className="w-full accent-emerald-500"
                  />
                  <div className="text-xs text-slate-500 mt-2 flex justify-between">
                    <span>允许穿模</span>
                    <span>剧烈排斥</span>
                  </div>
              </div>
            )}

            {/* 障碍物避障交互滑块 */}
            {slide.visualMode === 'interactive_avoidance' && (
              <div className="absolute bottom-6 right-6 z-10 bg-slate-900/90 p-5 rounded-xl border border-slate-700 shadow-2xl backdrop-blur-sm w-72">
                  <div className="flex justify-between items-center mb-3">
                      <span className="text-sm text-emerald-400 font-bold">避障排斥力 (Avoidance)</span>
                      <span className="text-sm text-slate-300 font-mono bg-slate-800 px-2 rounded">{avoForce}</span>
                  </div>
                  <input
                      type="range" min="0" max="150" value={avoForce}
                      onChange={(e) => setAvoForce(Number(e.target.value))}
                      className="w-full accent-emerald-500"
                  />
                  <div className="text-xs text-slate-500 mt-2 flex justify-between">
                    <span>贴墙摩擦</span>
                    <span>提前绕远</span>
                  </div>
              </div>
            )}

            {!['bilinear_demo', 'separation_demo', 'corner_demo', 'complexity_demo', 'agenda', 'interactive_separation', 'interactive_avoidance'].includes(slide.visualMode) && (
               <div className="absolute top-4 left-6 z-10">
                 <button
                   onClick={(e) => {
                     e.stopPropagation();
                     flowField.costField.fill(NORMAL_COST);
                     flowField.generateObstacles();
                     flowField.calculate();
                     setIsPlaying(false);
                     bfsProgressRef.current = 0;
                     particles.forEach(p => {
                        const pos = getRandomFreePos(flowField);
                        p.pos.x = pos.x;
                        p.pos.y = pos.y;
                        p.vel = { x: 0, y: 0 };
                     });
                   }}
                   className="bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white px-3 py-1.5 rounded-lg border border-slate-600 shadow-sm transition-colors text-sm font-medium flex items-center"
                 >
                   <RotateCcw className="w-4 h-4 mr-2" />
                   随机生成墙壁
                 </button>
               </div>
            )}
            
            <div className="relative rounded-xl overflow-hidden shadow-2xl border border-slate-700 ring-4 ring-slate-800/50 w-full h-full max-w-[800px] flex items-center justify-center">
              <canvas
                ref={canvasRef}
                width={CANVAS_WIDTH}
                height={CANVAS_HEIGHT}
                onClick={handleCanvasClick}
                className="bg-slate-900 cursor-crosshair block w-full h-auto"
              />
              
              {slide.visualMode === 'bfs_step' && (
                <div className="absolute bottom-6 left-1/2 -translate-x-1/2 flex space-x-3 bg-slate-900/80 p-2 rounded-xl backdrop-blur-sm border border-slate-700">
                  <button
                    onClick={(e) => { e.stopPropagation(); bfsProgressRef.current = 0; }}
                    className="bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded-lg flex items-center shadow-lg transition-colors font-medium text-sm"
                  >
                    <RotateCcw className="w-4 h-4 mr-2" />
                    重新生成动画
                  </button>
                </div>
              )}

              {(slide.visualMode === 'flow' || slide.visualMode === 'flow_large' || slide.visualMode === 'problem') && (
                <div className="absolute bottom-6 left-1/2 -translate-x-1/2 flex space-x-3 bg-slate-900/80 p-2 rounded-xl backdrop-blur-sm border border-slate-700">
                  <button
                    onClick={(e) => { e.stopPropagation(); setIsPlaying(!isPlaying); }}
                    className="bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded-lg flex items-center shadow-lg transition-colors font-medium text-sm"
                  >
                    {isPlaying ? <Pause className="w-4 h-4 mr-2" /> : <Play className="w-4 h-4 mr-2" />}
                    {isPlaying ? "暂停寻路" : "开始寻路"}
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setIsPlaying(false);
                      particles.forEach(p => {
                        const pos = getRandomFreePos(flowField);
                        p.pos.x = pos.x;
                        p.pos.y = pos.y;
                        p.vel = { x: 0, y: 0 };
                      });
                    }}
                    className="bg-slate-700 hover:bg-slate-600 text-white px-4 py-2 rounded-lg flex items-center shadow-lg transition-colors font-medium text-sm"
                  >
                    <RotateCcw className="w-4 h-4 mr-2" />
                    重置位置
                  </button>
                </div>
              )}
            </div>
            
            {!['bilinear_demo', 'separation_demo', 'corner_demo', 'complexity_demo', 'agenda', 'interactive_separation', 'interactive_avoidance'].includes(slide.visualMode) && (
              <div className="mt-6 flex space-x-6 text-sm text-slate-400">
                <div className="flex items-center"><div className="w-4 h-4 bg-[#ef4444] rounded-full mr-2"></div>目标点 (Target)</div>
                <div className="flex items-center"><div className="w-4 h-4 bg-[#334155] rounded mr-2"></div>障碍物 (Obstacles)</div>
                {(slide.visualMode === 'flow' || slide.visualMode === 'flow_large') && (
                  <div className="flex items-center"><div className="w-4 h-4 bg-[#3b82f6] rounded-full mr-2"></div>寻路单位 (Units)</div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      <div className="h-16 border-t border-slate-800 bg-slate-900 flex items-center justify-between px-6 shrink-0 relative">
        <div className="text-slate-500 text-sm">
          Use <kbd className="bg-slate-800 px-2 py-1 rounded">←</kbd> <kbd className="bg-slate-800 px-2 py-1 rounded">→</kbd> to navigate
        </div>
        
        <div className="flex items-center space-x-4">
          <button 
            onClick={handlePrev}
            disabled={currentSlide === 0}
            className="p-2 rounded-full hover:bg-slate-800 disabled:opacity-30 transition-colors"
          >
            <ChevronLeft className="w-6 h-6" />
          </button>
          <span className="text-slate-400 font-mono">
            {currentSlide + 1} / {SLIDES.length}
          </span>
          <button 
            onClick={handleNext}
            disabled={currentSlide === SLIDES.length - 1}
            className="p-2 rounded-full hover:bg-slate-800 disabled:opacity-30 transition-colors"
          >
            <ChevronRight className="w-6 h-6" />
          </button>
        </div>
      </div>

      {/* --- AI 演示助教 悬浮按钮 --- */}
      <button
        onClick={() => setIsChatOpen(!isChatOpen)}
        className={`fixed bottom-20 right-6 p-4 rounded-full shadow-2xl z-40 transition-all duration-300 ${isChatOpen ? 'bg-slate-700 text-white rotate-12 scale-90' : 'bg-emerald-600 hover:bg-emerald-500 text-white hover:scale-105'}`}
      >
        {isChatOpen ? <X className="w-6 h-6" /> : <MessageSquare className="w-6 h-6" />}
      </button>

      {/* --- AI 演示助教 聊天窗口 --- */}
      {isChatOpen && (
        <div className="fixed bottom-36 right-6 w-80 md:w-96 h-[450px] bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl z-50 flex flex-col overflow-hidden animate-in slide-in-from-bottom-5">
          <div className="flex items-center justify-between px-4 py-3 bg-slate-800 border-b border-slate-700">
            <div className="flex items-center space-x-2">
              <Bot className="w-5 h-5 text-emerald-400" />
              <span className="font-semibold text-slate-100 text-sm">AI 演示助教</span>
            </div>
            <span className="text-xs text-slate-500 bg-slate-900 px-2 py-1 rounded">根据当前PPT页作答</span>
          </div>
          
          <div className="flex-1 p-4 overflow-y-auto flex flex-col space-y-4 bg-slate-950 text-sm">
            {chatMessages.length === 0 && (
              <div className="text-slate-500 text-center mt-10 space-y-2">
                <Bot className="w-10 h-10 mx-auto text-slate-600 mb-2" />
                <p>我是你的向量场寻路专属 AI 助教。</p>
                <p>针对幻灯片第 {currentSlide + 1} 页的内容，有什么我可以帮忙解答的吗？</p>
              </div>
            )}
            {chatMessages.map((msg, i) => (
              <div key={i} className={`max-w-[85%] p-3 rounded-xl leading-relaxed ${msg.role === 'user' ? 'bg-emerald-600 text-white self-end rounded-br-none shadow-md' : 'bg-slate-800 text-slate-200 self-start border border-slate-700 rounded-bl-none shadow-sm'}`}>
                {msg.text}
              </div>
            ))}
            {isTyping && (
              <div className="bg-slate-800 text-slate-400 self-start p-3 rounded-xl border border-slate-700 rounded-bl-none flex items-center space-x-1.5 shadow-sm">
                <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-bounce"></div>
                <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-bounce" style={{ animationDelay: '0.15s' }}></div>
                <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-bounce" style={{ animationDelay: '0.3s' }}></div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>
          
          <div className="p-3 bg-slate-800 border-t border-slate-700 flex items-center space-x-2">
            <input
              type="text"
              value={chatInput}
              onChange={e => setChatInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleSendMessage()}
              placeholder="询问关于寻路算法的问题..."
              className="flex-1 bg-slate-900 border border-slate-600 rounded-lg px-3 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all placeholder:text-slate-500"
            />
            <button
              onClick={handleSendMessage}
              disabled={isTyping || !chatInput.trim()}
              className="p-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg disabled:opacity-50 transition-colors"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* 代码全屏放大弹窗 */}
      {expandedCode && (
        <div 
          className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-6"
          onClick={() => setExpandedCode(null)}
        >
          <div 
            className="relative w-full max-w-4xl max-h-[85vh] bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl flex flex-col overflow-hidden"
            onClick={e => e.stopPropagation()}
          >
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-950/50">
              <span className="text-emerald-400 font-mono text-sm uppercase tracking-wider font-semibold">Source Code</span>
              <button 
                onClick={() => setExpandedCode(null)}
                className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-8 overflow-auto">
              <pre className="text-base md:text-lg font-mono text-emerald-300 leading-relaxed whitespace-pre">
                <code>{expandedCode}</code>
              </pre>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}