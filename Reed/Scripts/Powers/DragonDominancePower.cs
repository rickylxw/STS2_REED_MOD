using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using STS2RitsuLib.Interop.AutoRegistration;
using STS2RitsuLib.Scaffolding.Content;
using System.Linq;
using Reed.Scripts.Powers;

namespace Reed.Scripts.Powers;

/// <summary>
/// 龙威（DragonDominancePower）——能力。
/// 每回合开始时，若所有敌人都带有灼燃，获得 Amount 层力量。
/// </summary>
[RegisterPower]
public sealed class DragonDominancePower : ModPowerTemplate
{
    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public override PowerAssetProfile AssetProfile => new(
        IconPath: $"{Entry.ResPath}/images/powers/{GetType().Name}.svg",
        BigIconPath: $"{Entry.ResPath}/images/powers/{GetType().Name}.svg");

    public override bool ShouldReceiveCombatHooks => true;

    public override async Task AfterPlayerTurnStart(PlayerChoiceContext choiceContext, Player player)
    {
        if (Amount <= 0) return;

        var enemies = ReedCombatHelper.GetEnemies(Owner);
        if (!enemies.Any()) return;

        foreach (var enemy in enemies)
        {
            if (ReedCombatHelper.GetPowerAmount<Scorch>(enemy) <= 0) return;
        }

        await PowerCmd.Apply<StrengthPower>(choiceContext, Owner, Amount, Owner, null);
    }
}
