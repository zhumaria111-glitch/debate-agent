import { useState } from 'react'

const allAwards = [
  { year: '2026', title: '抖音 AI 创变者计划黑客松联赛山东赛区三等奖', highlight: true },
  { year: '2026', title: '山东大学优秀党员', highlight: false },
  { year: '2025', title: '山东大学优秀毕业生', highlight: true },
  { year: '2024', title: '山东大学新百甘奖学金', highlight: true },
  { year: '2024', title: '特长奖学金二等奖 / 学业奖学金二等奖', highlight: false },
  { year: '2024', title: '山东省高校大学生跆拳道公开赛女子太极三章第六名、前踢铜牌', highlight: false },
  { year: '2023', title: '全国游泳锦标赛优秀志愿者', highlight: true },
  { year: '2023', title: '第一届山东大学文科实践创新大赛优胜奖', highlight: true },
  { year: '2023', title: '暑期社会实践获评省级优秀社会实践', highlight: true },
  { year: '2023', title: '优秀共青团员 / 特长奖学金 / 学业奖学金 / 优秀心理委员 / 先进个人', highlight: false },
  { year: '2022', title: '学业奖学金一等奖 / 校三好学生 / 院优秀学生干部 / 优秀志愿者', highlight: false },
  { year: '2022', title: '"同龄人"朋辈心理辅导技能大赛团队三等奖 + 个人三等奖', highlight: false },
  { year: '2021', title: '山东大学历史文化学院新生杯辩论赛一等奖', highlight: true },
]

export default function Awards() {
  const [expanded, setExpanded] = useState(false)
  const displayed = expanded ? allAwards : allAwards.filter(a => a.highlight)

  return (
    <section className="awards section" id="awards">
      <div className="section-label">Honors</div>
      <h2 className="section-title">荣誉奖项</h2>
      <div className="divider" />

      <div className="awards-grid">
        {displayed.map((award, i) => (
          <div
            className={`award-item${award.highlight ? ' award-highlight' : ''}`}
            key={i}
          >
            <span className="award-year">{award.year}</span>
            <span className="award-title">{award.title}</span>
          </div>
        ))}
      </div>

      <button className="btn btn-outline" onClick={() => setExpanded(!expanded)}>
        {expanded ? '收起' : `展开全部（共 ${allAwards.length} 条记录）`}
      </button>
    </section>
  )
}
