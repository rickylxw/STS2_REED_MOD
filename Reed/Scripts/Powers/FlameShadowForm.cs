using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.ValueProps;
using STS2RitsuLib.Interop.AutoRegistration;
using STS2RitsuLib.Scaffolding.Content;

namespace Reed.Scripts.Powers;

/// <summary>
/// 焰影形态（FlameShadowForm）—— 苇草的第二形态（拥有此能力即处于焰影形态）。
/// 每回合结束时，对所有敌人造成等于其灼燃层数的伤害。
/// 焰影形态下，灰烬不再提供格挡（Ash 中检查此能力）。
/// </summary>
[RegisterPower]
public sealed class FlameShadowForm : ModPowerTemplate
{
    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public override PowerAssetProfile AssetProfile => new(
        IconPath: $"{Entry.ResPath}/images/powers/{GetType().Name}.svg",
        BigIconPath: $"{Entry.ResPath}/images/powers/{GetType().Name}.svg");

    public override bool ShouldReceiveCombatHooks => true;

    /// <summary>
    /// 回合结束时：对所有敌人造成等于其灼燃层数的伤害。
    /// </summary>
    public override async Task AfterSideTurnEnd(PlayerChoiceContext choiceContext, CombatSide side, IEnumerable<Creature> participants)
    {
        if (Amount <= 0) return;
        if (!participants.Contains(Owner)) return;

        var enemies = ReedCombatHelper.GetEnemies(Owner);
        foreach (var enemy in enemies)
        {
            int scorchStacks = ReedCombatHelper.GetPowerAmount<Scorch>(enemy);
            if (scorchStacks > 0)
            {
                int damageAmount = scorchStacks;

                // 法术脆弱：受到的灼燃相关伤害 +50%
                if (ReedCombatHelper.HasPower<SpellVulnerable>(enemy))
                {
                    damageAmount = (int)Math.Ceiling(scorchStacks * 1.5m);
                }

                var damage = new DamageVar(damageAmount, ValueProp.Unpowered);
                await CreatureCmd.Damage(choiceContext, enemy, damage, null, null);
            }
        }
    }
}
