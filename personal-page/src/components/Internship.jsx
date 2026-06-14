export default function Internship() {
  return (
    <section className="internship section-alt" id="internship">
      <div className="section-inner">
        <div className="section-label">Experience</div>
        <h2 className="section-title">实习经历</h2>
        <div className="divider" />

        <div className="company-line">
          <img src="./jd.jpg" alt="京东" className="company-logo" />
          <div className="company-info">
            <span className="company-name">京东集团</span>
            <span className="sep-dot">·</span>
            <span>大时尚事业群 · 美妆业务部 · 助理采销</span>
            <span className="sep-dot">·</span>
            <span className="company-date">2026.01 — 2026.04</span>
          </div>
        </div>

        <div className="cards-row">
          <div className="card">
            <h3>流程优化</h3>
            <ul className="card-list">
              <li>建立<strong>商家分类管理体系</strong>，按品牌量级与配合度分层管理，差异化对接频率与支持力度</li>
              <li>梳理<strong>高频问题 Q&A 文档</strong>（审核驳回、价格异常、库存同步），覆盖 80% 以上日常咨询场景，新人上手时间从 2 周缩到 3 天</li>
              <li>统一<strong>作业模板</strong>（活动报名表、资源位申请表、品牌复盘报告），规范跨品牌对接标准</li>
            </ul>
          </div>
          <div className="card">
            <h3>核心项目</h3>
            <ul className="card-list">
              <li>统筹<strong>20+ 美妆品牌百补加赠项目</strong>：协调品牌方、平台运营、供应链三方，确认赠品库存、活动节奏、页面搭建全链路</li>
              <li><strong>LJQ 直播间价格对标</strong>：监控头部主播直播间价格策略，输出竞品价格日报，支撑采销谈判中的价格决策</li>
              <li><strong>美妆 × 鞋靴 CP 会场共建</strong>：跨品类联合营销，设计搭配场景提升连带率，协调两个事业群的资源位和选品逻辑</li>
            </ul>
          </div>
          <div className="card">
            <h3>业务理解</h3>
            <ul className="card-list">
              <li>掌握<strong>库存健康度</strong>分析：周转天数、滞销预警、安全库存线，从数据监控到主动预警</li>
              <li>理解<strong>供应链逻辑</strong>：采购在途、仓库间调拨、平行仓策略对履约成本和时效的影响</li>
              <li>学会用<strong>动销比例、毛利率、周转率</strong>评估品牌经营质量，而不仅是看 GMV</li>
            </ul>
          </div>
        </div>
      </div>
    </section>
  )
}
