(async function generateAUTeamLink() {
  console.log("⏳ 正在获取B Session Token...")

  // 自动获取登录凭证
  let accessToken
  try {
    const s = await fetch("/api/auth/session").then(r => r.json())
    accessToken = s?.accessToken
    if (!accessToken) throw new Error("accessToken 为空")
  } catch (e) {
    console.error("❌ 获取 Token 失败：", e.message)
    return
  }
  console.log("✅ Token 获取成功")

  const COUPON = "datroaica"

  // ---- 以下为你提供的 Payload（仅修改 workspace_name 动态生成）----
  const payload = {
    plan_name: "chatgptteamplan",
    team_plan_data: {
      workspace_name: "workspace", // 可自行修改
      price_interval: "month", // month 或 year
      seat_quantity: 2, // 席位数量，Team 最少 2？1的话是另外种玩法，需要号

    },
    billing_details: {
    country: "CA",
    currency: "CAD"
    },
    cancel_url: "https://chatgpt.com/?promoCode=datroaica",
    promo_code: COUPON,                            // 注意这里用的是 promo_code 字段
    checkout_ui_mode: "hosted"

  }

  console.log("⏳ 正在请求 Stripe 长链接 (US)...")
  try {
    const resp = await fetch(
      "https://chatgpt.com/backend-api/payments/checkout",
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${ accessToken }`,
      "Content-Type": "application/json"
},
  body: JSON.stringify(payload)
}
)
const data = await resp.json()

if (!resp.ok) {
  console.error(`❌ 请求失败 HTTP ${resp.status}`)
  console.log("📋 响应详情：", data)
  return
}

const hostedUrl = data?.url  || data?.stripe_hosted_url || data?.checkout_url
if (!hostedUrl) {
  console.warn("⚠️ 未找到长链接，原始响应：", data)
  returncd /home/wanglu/code/DQN/plumetracknets/code/ppo
  
  NUMPROC=1
  SAVEDIR=/mnt/hgfs/Desktop/RNN_OSL/trained_models/Test3Stage
  mkdir -p ${SAVEDIR}
  
  python -u main.py --env-name plume \
    --recurrent-policy \
    --dataset constantx20b5_s1 light_crosswindx20b5_s1 target_crosswindx20b5_s1 \
    --walking True \
    --env_dt 0.5 \
    --sim_steps_max 300 \
    --reset_offset_tmax 80 \
    --num-env-steps 10000 10000 10000 \
    --birthx 0.3 0.6 0.8 \
    --qvar 2.0 1.0 0.5 \
    --diff_max 0.8 0.8 0.8 \
    --diff_min 0.7 0.4 0.4 \
    --flipping True \
    --odor_scaling True \
    --r_shaping step oob \
    --algo ppo \
    --seed 137 \
    --squash_action True \
    --num-processes ${NUMPROC} \
    --num-mini-batch ${NUMPROC} \
    --rnn_type VRNN \
    --hidden_size 64 \
    --weight_decay 0.0001 \
    --eval_type skip \
    --save-dir ${SAVEDIR} \
    --outsuffix test_3stage \
    --use-gae --num-steps 2048 --lr 3e-4 --entropy-coef 0.005 --value-loss-coef 0.5 --ppo-epoch 10 --gamma 0.99 --gae-lambda 0.95 --use-linear-lr-decay
}

console.log("─".repeat(60))
console.log("✅ ChatGPT Team 链接生成成功！（美国）")
console.log("📋 Checkout Session ID :", data.checkout_session_id)
console.log("📌 计划                : ChatGPT Team (US/USD)")
console.log("💺 席位                :", payload.team_plan_data.seat_quantity)
console.log("🎟️  优惠码              :", COUPON)
console.log("🔗 Stripe 长链接：")
console.log(hostedUrl)
console.log("─".repeat(60));

} catch (e) {
  console.error("❌ 网络异常：", e.message)
}
}) ()