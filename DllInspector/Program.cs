using System;
using System.Reflection;
using System.Linq;
using System.Collections.Generic;

class Program
{
    static void Main()
    {
        string dataDir = @"E:\SteamLibrary\steamapps\common\Slay the Spire 2\data_sts2_windows_x86_64";
        string sts2Path = System.IO.Path.Combine(dataDir, "sts2.dll");
        string nugetPath = @"C:\Users\Administrator\.nuget\packages\sts2.ritsulib\0.5.18";
        string ritsuLibPath = System.IO.Path.Combine(nugetPath, "lib", "net9.0", "STS2-RitsuLib.dll");

        foreach (var dll in System.IO.Directory.GetFiles(dataDir, "*.dll"))
        {
            try { Assembly.LoadFrom(dll); } catch { }
        }
        var sts2Asm = Assembly.LoadFrom(sts2Path);
        var ritsuAsm = Assembly.LoadFrom(ritsuLibPath);

        var allAssemblies = new List<Assembly> { sts2Asm, ritsuAsm };
        IEnumerable<Type> AllTypes() => allAssemblies.SelectMany(a => { try { return a.GetTypes(); } catch { return Array.Empty<Type>(); } });

        // Dump PotionRarity and PotionUsage enum values
        Console.WriteLine("=== Potion Enums ===");
        foreach (var t in AllTypes().Where(t => t.Name == "PotionRarity" || t.Name == "PotionUsage" || t.Name == "TargetType"))
        {
            Console.WriteLine($"\nEnum: {t.FullName}");
            foreach (var v in Enum.GetValues(t))
            {
                Console.WriteLine($"  {v} = {(int)v}");
            }
        }

        // Inspect ModCharacterTemplate and its base types for StartingRelic properties
        Console.WriteLine("=== ModCharacterTemplate and base types: StartingRelic properties ===");
        foreach (var t in AllTypes().Where(t => t.Name.Contains("CharacterTemplate") || t.Name.Contains("CharacterModel")))
        {
            Console.WriteLine($"\nType: {t.FullName}");
            var props = t.GetProperties(BindingFlags.Public | BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.DeclaredOnly);
            foreach (var p in props)
            {
                if (p.Name.Contains("Relic") || p.Name.Contains("Starting"))
                {
                    Console.WriteLine($"  PROP: {p.Name} : {p.PropertyType} (CanRead={p.CanRead}, CanWrite={p.CanWrite}, Virtual={p.GetMethod?.IsVirtual})");
                }
            }
        }

        // Also check interfaces
        Console.WriteLine("\n=== Interfaces with Relic or Starting in name ===");
        foreach (var t in AllTypes().Where(t => t.IsInterface && (t.Name.Contains("Character") || t.Name.Contains("Relic"))))
        {
            Console.WriteLine($"\nInterface: {t.FullName}");
            var props = t.GetProperties();
            foreach (var p in props)
            {
                if (p.Name.Contains("Relic") || p.Name.Contains("Starting"))
                {
                    Console.WriteLine($"  PROP: {p.Name} : {p.PropertyType}");
                }
            }
        }

        // Inspect RunState and RunManager for Player access
        Console.WriteLine("\n=== RunState and RunManager ===");
        foreach (var t in AllTypes().Where(t => t.Name == "RunState" || t.Name == "RunManager" || t.Name == "IRunState"))
        {
            Console.WriteLine($"\nType: {t.FullName} (IsInterface={t.IsInterface})");
            var props = t.GetProperties(BindingFlags.Public | BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.DeclaredOnly);
            foreach (var p in props)
            {
                Console.WriteLine($"  PROP: {p.Name} : {p.PropertyType} (CanRead={p.CanRead}, CanWrite={p.CanWrite})");
            }
            var methods = t.GetMethods(BindingFlags.Public | BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.DeclaredOnly | BindingFlags.Static);
            foreach (var m in methods)
            {
                if (m.IsSpecialName) continue;
                var parms = string.Join(", ", m.GetParameters().Select(p => $"{p.ParameterType.Name} {p.Name}"));
                Console.WriteLine($"  METHOD: {m.Name}({parms}) -> {m.ReturnType.Name} [Static={m.IsStatic}]");
            }
        }

        // Search for static methods returning Player
        Console.WriteLine("\n=== Static methods returning Player ===");
        foreach (var t in AllTypes().Where(t => t.Name == "Player" || t.Name.Contains("PlayerAccess") || t.Name.Contains("GameAccess") || t.Name == "NGame" || t.Name.Contains("GameState")))
        {
            var methods = t.GetMethods(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static | BindingFlags.DeclaredOnly);
            foreach (var m in methods)
            {
                if (m.ReturnType.Name == "Player" || m.ReturnType.Name == "Player[]")
                {
                    var parms = string.Join(", ", m.GetParameters().Select(p => $"{p.ParameterType.Name} {p.Name}"));
                    Console.WriteLine($"  {t.FullName}.{m.Name}({parms}) -> {m.ReturnType.Name}");
                }
            }
        }

        // Inspect RelicSelectResult
        Console.WriteLine("\n=== RelicSelectResult ===");
        foreach (var t in AllTypes().Where(t => t.Name.Contains("RelicSelect")))
        {
            Console.WriteLine($"\nType: {t.FullName} (IsClass={t.IsClass}, IsInterface={t.IsInterface})");
            var props = t.GetProperties(BindingFlags.Public | BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.DeclaredOnly);
            foreach (var p in props)
            {
                Console.WriteLine($"  PROP: {p.Name} : {p.PropertyType}");
            }
            var methods = t.GetMethods(BindingFlags.Public | BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.DeclaredOnly | BindingFlags.Static);
            foreach (var m in methods)
            {
                if (m.IsSpecialName) continue;
                var parms = string.Join(", ", m.GetParameters().Select(p => $"{p.ParameterType.Name} {p.Name}"));
                Console.WriteLine($"  METHOD: {m.Name}({parms}) -> {m.ReturnType.Name} [Static={m.IsStatic}]");
            }
        }

        // Inspect RunStartedEvent
        Console.WriteLine("\n=== RunStartedEvent ===");
        foreach (var t in AllTypes().Where(t => t.Name.Contains("RunStarted") || t.Name.Contains("RunStart")))
        {
            Console.WriteLine($"\nType: {t.FullName} (IsClass={t.IsClass}, IsInterface={t.IsInterface})");
            var props = t.GetProperties(BindingFlags.Public | BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.DeclaredOnly);
            foreach (var p in props)
            {
                Console.WriteLine($"  PROP: {p.Name} : {p.PropertyType} (CanRead={p.CanRead})");
            }
            var fields = t.GetFields(BindingFlags.Public | BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.DeclaredOnly);
            foreach (var f in fields)
            {
                Console.WriteLine($"  FIELD: {f.Name} : {f.FieldType}");
            }
        }

        // Inspect RelicSelectCmd
        Console.WriteLine("\n=== RelicSelectCmd ===");
        foreach (var t in AllTypes().Where(t => t.Name == "RelicSelectCmd" || t.Name == "RelicCmd"))
        {
            Console.WriteLine($"\nType: {t.FullName}");
            var methods = t.GetMethods(BindingFlags.Public | BindingFlags.Static | BindingFlags.DeclaredOnly);
            foreach (var m in methods)
            {
                if (m.IsSpecialName) continue;
                var parms = string.Join(", ", m.GetParameters().Select(p => $"{p.ParameterType.Name} {p.Name}"));
                Console.WriteLine($"  METHOD: {m.Name}({parms}) -> {m.ReturnType.Name} [Static={m.IsStatic}]");
            }
        }

        // Inspect ModCharacterTemplate base hierarchy
        Console.WriteLine("\n=== ModCharacterTemplate base hierarchy ===");
        foreach (var t in AllTypes().Where(t => t.Name.Contains("CharacterTemplate") || t.Name == "CharacterModel"))
        {
            Console.WriteLine($"\nType: {t.FullName}");
            var baseType = t.BaseType;
            while (baseType != null)
            {
                Console.WriteLine($"  -> base: {baseType.FullName}");
                baseType = baseType.BaseType;
            }
            var interfaces = t.GetInterfaces();
            foreach (var i in interfaces)
            {
                Console.WriteLine($"  -> interface: {i.FullName}");
            }
        }

        // Inspect SubscribeLifecycle overloads
        Console.WriteLine("\n=== SubscribeLifecycle ===");
        foreach (var t in AllTypes().Where(t => t.Name.Contains("RitsuLib") || t.Name == "RitsuLibFramework" || t.Name.Contains("Lifecycle")))
        {
            if (t.Name != "RitsuLibFramework") continue;
            Console.WriteLine($"\nType: {t.FullName}");
            var methods = t.GetMethods(BindingFlags.Public | BindingFlags.Static | BindingFlags.DeclaredOnly);
            foreach (var m in methods)
            {
                if (m.Name.Contains("Subscribe"))
                {
                    var parms = string.Join(", ", m.GetParameters().Select(p => $"{p.ParameterType.Name} {p.Name}"));
                    Console.WriteLine($"  METHOD: {m.Name}({parms}) -> {m.ReturnType.Name}");
                }
            }
        }

        // Inspect ModelDb methods
        Console.WriteLine("\n=== ModelDb methods ===");
        foreach (var t in AllTypes().Where(t => t.Name == "ModelDb"))
        {
            Console.WriteLine($"\nType: {t.FullName}");
            var methods = t.GetMethods(BindingFlags.Public | BindingFlags.Static | BindingFlags.DeclaredOnly);
            foreach (var m in methods)
            {
                if (m.IsSpecialName) continue;
                var parms = string.Join(", ", m.GetParameters().Select(p => $"{p.ParameterType.Name} {p.Name}"));
                Console.WriteLine($"  METHOD: {m.Name}({parms}) -> {m.ReturnType.Name} [Static={m.IsStatic}]");
            }
        }

        // Inspect RelicModel and ModRelicTemplate base hierarchy
        Console.WriteLine("\n=== RelicModel / ModRelicTemplate hierarchy ===");
        foreach (var t in AllTypes().Where(t => t.Name == "RelicModel" || t.Name == "ModRelicTemplate" || t.Name.Contains("RelicTemplate") || t.Name == "SingletonModel"))
        {
            Console.WriteLine($"\nType: {t.FullName}");
            var baseType = t.BaseType;
            while (baseType != null)
            {
                Console.WriteLine($"  -> base: {baseType.FullName}");
                baseType = baseType.BaseType;
            }
            var interfaces = t.GetInterfaces();
            foreach (var i in interfaces)
            {
                Console.WriteLine($"  -> interface: {i.FullName}");
            }
        }

        // Inspect ALL virtual methods on ModRelicTemplate and RelicModel
        Console.WriteLine("\n=== ModRelicTemplate + RelicModel ALL virtual methods ===");
        foreach (var t in AllTypes().Where(t => t.Name == "ModRelicTemplate" || t.Name == "RelicModel"))
        {
            Console.WriteLine($"\nType: {t.FullName}");
            var methods = t.GetMethods(BindingFlags.Public | BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.DeclaredOnly);
            foreach (var m in methods)
            {
                if (m.IsSpecialName) continue;
                var parms = string.Join(", ", m.GetParameters().Select(p => $"{p.ParameterType.Name} {p.Name}"));
                Console.WriteLine($"  METHOD: {m.Name}({parms}) -> {m.ReturnType.Name} [Virtual={m.IsVirtual}, Abstract={m.IsAbstract}]");
            }
            var props = t.GetProperties(BindingFlags.Public | BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.DeclaredOnly);
            foreach (var p in props)
            {
                Console.WriteLine($"  PROP: {p.Name} : {p.PropertyType} [Virtual={p.GetMethod?.IsVirtual}]");
            }
        }

        // Inspect ALL lifecycle event types
        Console.WriteLine("\n=== ALL Lifecycle Events ===");
        foreach (var t in AllTypes().Where(t => t.Namespace != null && t.Namespace.Contains("STS2RitsuLib") && (t.Name.Contains("Event") || t.Name.Contains("Lifecycle"))))
        {
            Console.WriteLine($"\nType: {t.FullName} (IsClass={t.IsClass}, IsInterface={t.IsInterface}, IsStruct={!t.IsClass && !t.IsInterface && t.IsValueType})");
            var props = t.GetProperties(BindingFlags.Public | BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.DeclaredOnly);
            foreach (var p in props)
            {
                Console.WriteLine($"  PROP: {p.Name} : {p.PropertyType}");
            }
            var fields = t.GetFields(BindingFlags.Public | BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.DeclaredOnly);
            foreach (var f in fields)
            {
                Console.WriteLine($"  FIELD: {f.Name} : {f.FieldType}");
            }
        }

        // Inspect RelicModel events (add_RelicObtained etc.)
        Console.WriteLine("\n=== Player Relic Events ===");
        foreach (var t in AllTypes().Where(t => t.Name == "Player"))
        {
            Console.WriteLine($"\nType: {t.FullName}");
            var events = t.GetEvents(BindingFlags.Public | BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.DeclaredOnly);
            foreach (var e in events)
            {
                Console.WriteLine($"  EVENT: {e.Name} : {e.EventHandlerType}");
            }
            var methods = t.GetMethods(BindingFlags.Public | BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.DeclaredOnly);
            foreach (var m in methods)
            {
                if (m.IsSpecialName) continue;
                if (m.Name.Contains("Relic") || m.Name.Contains("Obtain"))
                {
                    var parms = string.Join(", ", m.GetParameters().Select(p => $"{p.ParameterType.Name} {p.Name}"));
                    Console.WriteLine($"  METHOD: {m.Name}({parms}) -> {m.ReturnType.FullName} [Static={m.IsStatic}]");
                }
            }
        }

        // Inspect CharacterModel ALL virtual methods
        Console.WriteLine("\n=== CharacterModel ALL methods ===");
        foreach (var t in AllTypes().Where(t => t.Name == "CharacterModel" || t.Name == "ModCharacterTemplate"))
        {
            Console.WriteLine($"\nType: {t.FullName}");
            var methods = t.GetMethods(BindingFlags.Public | BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.DeclaredOnly);
            foreach (var m in methods)
            {
                if (m.IsSpecialName) continue;
                var parms = string.Join(", ", m.GetParameters().Select(p => $"{p.ParameterType.Name} {p.Name}"));
                Console.WriteLine($"  METHOD: {m.Name}({parms}) -> {m.ReturnType.Name} [Virtual={m.IsVirtual}, Abstract={m.IsAbstract}]");
            }
            var props = t.GetProperties(BindingFlags.Public | BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.DeclaredOnly);
            foreach (var p in props)
            {
                Console.WriteLine($"  PROP: {p.Name} : {p.PropertyType.Name} [Virtual={p.GetMethod?.IsVirtual}]");
            }
        }

        // Inspect FromChooseARelicScreen full return type
        Console.WriteLine("\n=== RelicSelectCmd full method details ===");
        foreach (var t in AllTypes().Where(t => t.Name == "RelicSelectCmd"))
        {
            Console.WriteLine($"\nType: {t.FullName}");
            var methods = t.GetMethods(BindingFlags.Public | BindingFlags.Static | BindingFlags.DeclaredOnly);
            foreach (var m in methods)
            {
                if (m.IsSpecialName) continue;
                var parms = string.Join(", ", m.GetParameters().Select(p => $"{p.ParameterType.FullName} {p.Name}"));
                Console.WriteLine($"  METHOD: {m.Name}({parms}) -> {m.ReturnType.FullName} [Static={m.IsStatic}]");
            }
        }

        // Inspect RelicCmd full method details
        Console.WriteLine("\n=== RelicCmd full method details ===");
        foreach (var t in AllTypes().Where(t => t.Name == "RelicCmd"))
        {
            Console.WriteLine($"\nType: {t.FullName}");
            var methods = t.GetMethods(BindingFlags.Public | BindingFlags.Static | BindingFlags.DeclaredOnly);
            foreach (var m in methods)
            {
                if (m.IsSpecialName) continue;
                var parms = string.Join(", ", m.GetParameters().Select(p => $"{p.ParameterType.FullName} {p.Name}"));
                Console.WriteLine($"  METHOD: {m.Name}({parms}) -> {m.ReturnType.FullName} [Static={m.IsStatic}]");
            }
        }

        // Search for ALL events/types containing "Run" in STS2RitsuLib namespace
        Console.WriteLine("\n=== ALL STS2RitsuLib types (full list) ===");
        foreach (var t in AllTypes().Where(t => t.Namespace != null && t.Namespace.Contains("STS2RitsuLib")))
        {
            Console.WriteLine($"  {t.FullName} (IsClass={t.IsClass}, IsStruct={t.IsValueType && !t.IsEnum}, IsEnum={t.IsEnum})");
        }

        // Check Player.CreateForNewRun and PopulateStartingRelics
        Console.WriteLine("\n=== Player creation and starting relic methods ===");
        foreach (var t in AllTypes().Where(t => t.Name == "Player"))
        {
            Console.WriteLine($"\nType: {t.FullName}");
            var methods = t.GetMethods(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static | BindingFlags.DeclaredOnly);
            foreach (var m in methods)
            {
                if (m.IsSpecialName) continue;
                var parms = string.Join(", ", m.GetParameters().Select(p => $"{p.ParameterType.FullName} {p.Name}"));
                Console.WriteLine($"  STATIC METHOD: {m.Name}({parms}) -> {m.ReturnType.FullName}");
            }
            methods = t.GetMethods(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance | BindingFlags.DeclaredOnly);
            foreach (var m in methods)
            {
                if (m.IsSpecialName) continue;
                if (m.Name.Contains("Start") || m.Name.Contains("Populate") || m.Name.Contains("Begin") || m.Name.Contains("Init"))
                {
                    var parms = string.Join(", ", m.GetParameters().Select(p => $"{p.ParameterType.FullName} {p.Name}"));
                    Console.WriteLine($"  INSTANCE METHOD: {m.Name}({parms}) -> {m.ReturnType.FullName}");
                }
            }
        }

        // === NEW: CardVisualStyle enum ===
        Console.WriteLine("\n=== CardVisualStyle enum ===");
        foreach (var t in AllTypes().Where(t => t.Name == "CardVisualStyle"))
        {
            Console.WriteLine($"\nEnum: {t.FullName}");
            foreach (var v in Enum.GetValues(t))
            {
                Console.WriteLine($"  {v} = {(int)v}");
            }
        }

        // === NEW: All RitsuLib types containing "Character" ===
        Console.WriteLine("\n=== All RitsuLib types containing 'Character' ===");
        foreach (var t in AllTypes().Where(t => t.Namespace != null && t.Namespace.Contains("STS2RitsuLib") && t.Name.Contains("Character")))
        {
            Console.WriteLine($"  {t.FullName} (IsClass={t.IsClass}, IsInterface={t.IsInterface}, IsEnum={t.IsEnum})");
        }

        // === NEW: Full dump of CharacterTemplate types ===
        Console.WriteLine("\n=== Full dump of CharacterTemplate types ===");
        foreach (var t in AllTypes().Where(t => t.Name.Contains("CharacterTemplate") || t.Name.Contains("CharacterModel")))
        {
            Console.WriteLine($"\nType: {t.FullName} (Base={t.BaseType?.FullName})");
            // Walk up the hierarchy and dump all props/methods
            var hierarchyTypes = new List<Type>();
            var current = t;
            while (current != null)
            {
                hierarchyTypes.Add(current);
                current = current.BaseType;
            }
            foreach (var ht in hierarchyTypes)
            {
                var props = ht.GetProperties(BindingFlags.Public | BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.DeclaredOnly);
                foreach (var p in props)
                {
                    Console.WriteLine($"  PROP: {p.Name} : {p.PropertyType.FullName} [Virtual={p.GetMethod?.IsVirtual}, DeclaredIn={ht.Name}]");
                }
                var methods = ht.GetMethods(BindingFlags.Public | BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.DeclaredOnly);
                foreach (var m in methods)
                {
                    if (m.IsSpecialName) continue;
                    var parms = string.Join(", ", m.GetParameters().Select(p => $"{p.ParameterType.Name} {p.Name}"));
                    Console.WriteLine($"  METHOD: {m.Name}({parms}) -> {m.ReturnType.Name} [Virtual={m.IsVirtual}, Abstract={m.IsAbstract}, DeclaredIn={ht.Name}]");
                }
            }
        }

        // === NEW: Types containing "Stained", "Tome", "Ancient" in name ===
        Console.WriteLine("\n=== Types containing 'Stained', 'Tome', 'AncientCard' in name ===");
        foreach (var t in AllTypes().Where(t => t.Name.Contains("Stained") || t.Name.Contains("Tome") || t.Name.Contains("AncientCard")))
        {
            Console.WriteLine($"\nType: {t.FullName} (IsClass={t.IsClass}, IsEnum={t.IsEnum})");
            var props = t.GetProperties(BindingFlags.Public | BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.DeclaredOnly);
            foreach (var p in props)
            {
                Console.WriteLine($"  PROP: {p.Name} : {p.PropertyType.Name}");
            }
            var fields = t.GetFields(BindingFlags.Public | BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.DeclaredOnly);
            foreach (var f in fields)
            {
                Console.WriteLine($"  FIELD: {f.Name} : {f.FieldType.Name}");
            }
            var methods = t.GetMethods(BindingFlags.Public | BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.DeclaredOnly);
            foreach (var m in methods)
            {
                if (m.IsSpecialName) continue;
                var parms = string.Join(", ", m.GetParameters().Select(p => $"{p.ParameterType.Name} {p.Name}"));
                Console.WriteLine($"  METHOD: {m.Name}({parms}) -> {m.ReturnType.Name}");
            }
        }

        // === NEW: Search ALL types for methods/props containing "AncientCard" or "TomeCard" ===
        Console.WriteLine("\n=== ALL methods/props containing 'AncientCard' or 'TomeCard' ===");
        foreach (var t in AllTypes())
        {
            var props = t.GetProperties(BindingFlags.Public | BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.DeclaredOnly);
            foreach (var p in props)
            {
                if (p.Name.Contains("AncientCard") || p.Name.Contains("TomeCard"))
                {
                    Console.WriteLine($"  {t.FullName}.PROP: {p.Name} : {p.PropertyType.FullName}");
                }
            }
            var methods = t.GetMethods(BindingFlags.Public | BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.DeclaredOnly);
            foreach (var m in methods)
            {
                if (m.Name.Contains("AncientCard") || m.Name.Contains("TomeCard"))
                {
                    var parms = string.Join(", ", m.GetParameters().Select(p => $"{p.ParameterType.Name} {p.Name}"));
                    Console.WriteLine($"  {t.FullName}.METHOD: {m.Name}({parms}) -> {m.ReturnType.Name}");
                }
            }
        }

        // === NEW: Search for StainedBook relic model ===
        Console.WriteLine("\n=== Relic models containing 'Stained' or 'Book' ===");
        foreach (var t in AllTypes().Where(t => t.Name.Contains("Stained") || (t.Name.Contains("Book") && t.Namespace != null && t.Namespace.Contains("MegaCrit"))))
        {
            Console.WriteLine($"\nType: {t.FullName}");
            var methods = t.GetMethods(BindingFlags.Public | BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.DeclaredOnly);
            foreach (var m in methods)
            {
                if (m.IsSpecialName) continue;
                var parms = string.Join(", ", m.GetParameters().Select(p => $"{p.ParameterType.Name} {p.Name}"));
                Console.WriteLine($"  METHOD: {m.Name}({parms}) -> {m.ReturnType.Name} [Virtual={m.IsVirtual}]");
            }
            var props = t.GetProperties(BindingFlags.Public | BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.DeclaredOnly);
            foreach (var p in props)
            {
                Console.WriteLine($"  PROP: {p.Name} : {p.PropertyType.Name}");
            }
        }

        // === NEW: All RitsuLib types (complete list) ===
        Console.WriteLine("\n=== All RitsuLib types (complete list) ===");
        foreach (var t in AllTypes().Where(t => t.Namespace != null && t.Namespace.Contains("STS2RitsuLib")))
        {
            Console.WriteLine($"  {t.FullName}");
        }
    }
}
