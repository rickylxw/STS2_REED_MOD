using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using STS2RitsuLib.Interop.AutoRegistration;
using STS2RitsuLib.Scaffolding.Content;

namespace Reed.Scripts.Powers;

/// <summary>
/// 同燃共阵（UnitedFrontPower）——联机专属能力。
/// 每回合开始时，对所有敌人施加灼燃，层数 = 友方数量 × 能力层数。
/// 联机模式中友方数量越多，灼燃层数越高。
/// </summary>
[RegisterPower]
public sealed class UnitedFrontPower : ModPowerTemplate
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

        int allyCount = ReedCombatHelper.GetAllies(Owner).Count();
        int scorchAmount = allyCount * Amount;
        if (scorchAmount <= 0) return;

        var enemies = ReedCombatHelper.GetEnemies(Owner);
        foreach (var enemy in enemies)
        {
            await PowerCmd.Apply<Scorch>(choiceContext, enemy, scorchAmount, Owner, null);
        }
    }
}
