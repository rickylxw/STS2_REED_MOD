using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using STS2RitsuLib.Interop.AutoRegistration;
using STS2RitsuLib.Scaffolding.Content;
using Reed.Scripts.Powers;

namespace Reed.Scripts.Powers;

/// <summary>
/// 风助火势（WindblazePower）——能力。
/// 每个玩家回合结束时，所有敌人获得 Amount 层灼燃。
/// </summary>
[RegisterPower]
public sealed class WindblazePower : ModPowerTemplate
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
        foreach (var enemy in enemies)
        {
            if (enemy.IsAlive)
            {
                await PowerCmd.Apply<Scorch>(choiceContext, enemy, Amount, Owner, null);
            }
        }
    }
}
