# JavaFX → WPF Interaction Compatibility Contract

| MAP ID | JavaFX mechanism | Current observable behavior | WPF mechanism/decision | Required parity | UI/NFR oracle | Owner | Status |
|---|---|---|---|---|---|---|---|
| MAP-UI-001 | Application Thread / Platform.runLater | | Dispatcher/InvokeAsync/Task | ordering, responsiveness, error | | | open |
| MAP-UI-002 | Property/Binding/ObservableValue | | CLR/DependencyProperty/INotifyPropertyChanged/Binding | update timing, lazy/eager, listener lifetime | | | open |
| MAP-UI-003 | ObservableList/SortedList/FilteredList | | ObservableCollection/ICollectionView | order/filter/group/change | | | open |
| MAP-UI-004 | FXML/controller/include | | XAML/View/ViewModel/resource | lifecycle, injection, lookup | | | open |
| MAP-UI-005 | CSS/pseudo-class/theme | | ResourceDictionary/Style/Trigger/VisualState | precedence/state/theme | | | open |
| MAP-UI-006 | event filter/handler/bubbling | | routed preview/bubble event/command | order, consume/cancel | | | open |
| MAP-UI-007 | focus/traversal/accelerator/IME | | WPF focus/navigation/input binding | keyboard-only parity | | | open |
| MAP-UI-008 | Stage/Scene/modal/dialog/nested loop | | Window/owner/ShowDialog/Dispatcher frame | ownership, close, blocking | | | open |
| MAP-UI-009 | Task/Service/progress/cancel | | async command/Task/cancellation | state, retry, cancel, exception | | | open |
| MAP-UI-010 | TableView/TreeView/edit/selection/virtualization | | WPF controls/virtualization | large data, edit commit, selection | | | open |
| MAP-UI-011 | WebView/media/Swing/native interop | | WebView2/media/interop/replacement | capability/security/deploy | | | open |
| MAP-UI-012 | clipboard/drag-drop/print/file chooser/tray | | WPF/Win32 APIs | format, permission, cancel | | | open |
| MAP-UI-013 | accessibility/localization/DPI/font | | AutomationPeer/resources/per-monitor DPI | assistive tech and layout | | | open |
| MAP-UI-014 | animation/timeline/pulse | | storyboard/rendering timer | timing/CPU/reduced motion | | | open |
| MAP-UI-015 | shutdown/implicitExit/window close | | Application shutdown/session ending | prompt/save/cancel/order | | | open |

The WPF threading model uses a Dispatcher and thread-affine UI objects; JavaFX scene graph changes are similarly constrained to the JavaFX Application Thread. Preserve observable ordering and cancellation, not API names.

