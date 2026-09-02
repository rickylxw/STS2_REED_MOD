using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Potions;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using STS2RitsuLib.Interop.AutoRegistration;
using STS2RitsuLib.Scaffolding.Content;
using Reed.Scripts.Character;
using Reed.Scripts.Powers;

namespace Reed.Scripts.Potions;

/// <summary>
/// 龙焰药水（DragonFlamePotion）。
/// 对所有敌人施加5层灼燃，并获得2层灰烬。
/// </summary>
[RegisterPotion(typeof(ReedPotionPool))]
public sealed class DragonFlamePotion : ModPotionTemplate
{
    public override PotionRarity Rarity => PotionRarity.Uncommon;
    public override PotionUsage Usage => PotionUsage.CombatOnly;
    public override MegaCrit.Sts2.Core.Entities.Cards.TargetType TargetType => MegaCrit.Sts2.Core.Entities.Cards.TargetType.Self;

    public override PotionAssetProfile AssetProfile => new(
        ImagePath: $"{Entry.ResPath}/images/potions/{GetType().Name}.svg",
        OutlinePath: $"{Entry.ResPath}/images/potions/{GetType().Name}.svg");

    protected override async Task OnUse(PlayerChoiceContext choiceContext, Creature? target)
    {
        // 对所有敌人施加5层灼燃
        var enemies = ReedCombatHelper.GetEnemies(target);
        foreach (var enemy in enemies)
        {
            await PowerCmd.Apply<Scorch>(choiceContext, enemy, 5, target, null);
        }

        // 获得2层灰烬
        await PowerCmd.Apply<Ash>(choiceContext, target, 2, target, null);
    }
}
