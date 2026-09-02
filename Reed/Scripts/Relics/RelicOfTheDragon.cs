using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.ValueProps;
using STS2RitsuLib.Interop.AutoRegistration;
using STS2RitsuLib.Scaffolding.Content;

namespace Reed.Scripts.Relics;

/// <summary>
/// 榫欎箣閬楃墿锛圧elicOfTheDragon锛夆€斺€?绋€鏈夐仐鐗┿€?/// 姣忓洖鍚堝紑濮嬫椂锛岃幏寰?鐐瑰姏閲忋€?/// </summary>
[RegisterRelic(typeof(ReedRelicPool))]
public sealed class RelicOfTheDragon : ModRelicTemplate
{
    public override RelicRarity Rarity => RelicRarity.Rare;

    public override RelicAssetProfile AssetProfile => new(
        IconPath: $"{Entry.ResPath}/images/relics/{GetType().Name}.svg",
        IconOutlinePath: $"{Entry.ResPath}/images/relics/{GetType().Name}.svg",
        BigIconPath: $"{Entry.ResPath}/images/relics/{GetType().Name}.svg");

    public override bool ShouldReceiveCombatHooks => true;

    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new CardsVar(1) // 鍔涢噺灞傛暟
    ];

    public override async Task AfterPlayerTurnStart(PlayerChoiceContext choiceContext, Player player)
    {
        await PowerCmd.Apply<StrengthPower>(choiceContext, Owner.Creature, DynamicVars.Cards.IntValue, Owner.Creature, null);
    }
}

