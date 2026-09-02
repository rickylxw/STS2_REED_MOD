using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.ValueProps;
using STS2RitsuLib.Interop.AutoRegistration;
using STS2RitsuLib.Scaffolding.Content;

namespace Reed.Scripts.Powers;

/// <summary>
/// 灼燃（Scorch）—— 焰影苇草的核心机制。
/// 敌人身上的 Debuff：回合结束时每层造成1点不可格挡伤害，层数减1。
/// 玩家身上的灼燃请用 ScorchCounter（Buff 版）。
/// </summary>
[RegisterPower]
public sealed class Scorch : ModPowerTemplate
{
    public override PowerType Type => PowerType.Debuff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public override PowerAssetProfile AssetProfile => new(
        IconPath: $"{Entry.ResPath}/images/powers/{GetType().Name}.svg",
        BigIconPath: $"{Entry.ResPath}/images/powers/{GetType().Name}.svg");

    public override bool ShouldReceiveCombatHooks => true;

    public override async Task AfterSideTurnEnd(PlayerChoiceContext choiceContext, CombatSide side, IEnumerable<Creature> participants)
    {
        if (Amount <= 0) return;
        if (side != CombatSide.Enemy) return;

        // 灼燃免疫：不造成伤害，但层数仍衰减
        if (!ReedCombatHelper.HasPower<ScorchImmunity>(Owner))
        {
            var damage = new DamageVar(Amount, ValueProp.Unpowered | ValueProp.Unblockable);
            await CreatureCmd.Damage(choiceContext, Owner, damage, null, null);
        }

        // 层数减少1
        SetAmount(Amount - 1, false);
    }
}
