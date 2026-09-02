using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.ValueProps;
using STS2RitsuLib.Interop.AutoRegistration;
using STS2RitsuLib.Scaffolding.Content;

namespace Reed.Scripts.Relics;

/// <summary>
/// 浣欑儸涔嬪績锛圚eartOfEmbers锛夆€斺€?涓嶅父瑙侀仐鐗┿€?/// 姣忓洖鍚堝紑濮嬫椂锛岃幏寰?鐐规牸鎸°€?/// </summary>
[RegisterRelic(typeof(ReedRelicPool))]
public sealed class HeartOfEmbers : ModRelicTemplate
{
    public override RelicRarity Rarity => RelicRarity.Uncommon;

    public override RelicAssetProfile AssetProfile => new(
        IconPath: $"{Entry.ResPath}/images/relics/{GetType().Name}.svg",
        IconOutlinePath: $"{Entry.ResPath}/images/relics/{GetType().Name}.svg",
        BigIconPath: $"{Entry.ResPath}/images/relics/{GetType().Name}.svg");

    public override bool ShouldReceiveCombatHooks => true;

    protected override IEnumerable<DynamicVar> CanonicalVars =>
    [
        new BlockVar(3m, ValueProp.Move) // 格挡值
    ];

    public override async Task AfterPlayerTurnStart(PlayerChoiceContext choiceContext, Player player)
    {
        // TODO: 楠岃瘉閬楃墿涓幏寰楁牸鎸＄殑 API锛坈ardPlay 鍙傛暟鍙兘闇€瑕?null锛?        await CreatureCmd.GainBlock(Owner.Creature, DynamicVars.Block, null);
    }
}

