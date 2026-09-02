using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.ValueProps;
using STS2RitsuLib.Interop.AutoRegistration;
using STS2RitsuLib.Scaffolding.Content;

namespace Reed.Scripts.Powers;

/// <summary>
/// 不灭之焰（EverflamePower）——能力。
/// 每回合结束时，若有敌人带有灼燃，获得1层灰烬（层数等于能力层数）。
/// </summary>
[RegisterPower]
public sealed class EverflamePower : ModPowerTemplate
{
    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public override PowerAssetProfile AssetProfile => new(
        IconPath: $"{Entry.ResPath}/images/powers/{GetType().Name}.svg",
        BigIconPath: $"{Entry.ResPath}/images/powers/{GetType().Name}.svg");

    public override bool ShouldReceiveCombatHooks => true;

    public override async Task AfterSideTurnEnd(PlayerChoiceContext choiceContext, CombatSide side, IEnumerable<Creature> participants)
    {
        if (Amount <= 0) return;
        if (side != CombatSide.Player) return;

        var enemies = ReedCombatHelper.GetEnemies(Owner);
        bool anyScorched = false;
        foreach (var enemy in enemies)
        {
            if (ReedCombatHelper.GetPowerAmount<Scorch>(enemy) > 0)
            {
                anyScorched = true;
                break;
            }
        }

        if (anyScorched)
        {
            await PowerCmd.Apply<Ash>(choiceContext, Owner, Amount, Owner, null);
        }
    }
}
